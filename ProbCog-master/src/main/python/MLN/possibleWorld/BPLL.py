# -*- coding: iso-8859-1 -*-
#
# Markov Logic Networks
#
# (C) 2006-2012 by Dominik Jain (jain@cs.tum.edu)
# 
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

from AbstractLearner import AbstractLearner, SoftEvidenceLearner
from collections import defaultdict
from MLN.util import *
import numpy


class BPLL(AbstractLearner):
    '''
    Pseudo-log-likelihood learning with blocking, i.e. a generalisation
    of PLL which takes into consideration the fact that the truth value of a
    blocked atom cannot be inverted without changing a further atom's truth
    value from the same block.
    This learner is fairly efficient, as it computes f and grad based only
    on a sufficient statistic.
    Furthermore, it is memory-efficient, as it does not require the list of
    ground formulas in memory; it will only iterate over all the groundings.
    '''    
    
    groundingMethod = 'GroundedAtomsGroundFormulasIterableFactory'
    
    def __init__(self, mrf, **params):
        AbstractLearner.__init__(self, mrf, **params)
        
    def _isQueryVar(self, idxVar):
        return True # for non-discriminative learning, all variables are relevant

    def _prepareOpt(self):
        print "constructing blocks..."
        self.mrf._getPllBlocks()
        self.mrf._getAtom2BlockIdx()        
        self._computeStatistics()
        # remove data that is now obsolete
        self.mrf.atom2BlockIdx = None
    
    def _addMBCount(self, idxVar, size, idxValue, idxWeight, increment=1):
        self.blockRelevantFormulas[idxVar].add(idxWeight)
        d = self.fcounts.get(idxWeight)
        if d is None:
            d = {}
            self.fcounts[idxWeight] = d
        if idxVar not in d:
            d[idxVar] = numpy.zeros(size)
        d[idxVar][idxValue] += increment
        #print "adding %f to %d/%d" % (increment, idxVar, idxValue)

    def _getBlockProbMB(self, idxVar, wt):        
        (idxGA, block) = self.mrf.pllBlocks[idxVar]
        numValues = 2 if idxGA is not None else len(block)
        
        relevantFormulas = self.blockRelevantFormulas.get(idxVar, None)
        if relevantFormulas is None: # no list was saved, so the truth of all formulas is unaffected by the variable's value
            # uniform distribution applies
            p = 1.0/numValues
            return numpy.repeat(p, numValues)
        
        sums = numpy.zeros(numValues)
        for idxFormula in relevantFormulas:            
            for idxValue, n in enumerate(self.fcounts[idxFormula][idxVar]):
                sums[idxValue] += n * wt[idxFormula]
        sum_min = numpy.min(sums)
        sums -= sum_min
        sum_max = numpy.max(sums)
        sums -= sum_max
        expsums = numpy.sum(numpy.exp(sums))
        s = numpy.log(expsums)
        return numpy.exp(sums - s)
    
    def _calculateBlockProbsMB(self, wt):
        if ('wtsLastBlockProbMBComputation' not in dir(self)) or self.wtsLastBlockProbMBComputation != list(wt):
            print "recomputing block probabilities..."
            self.__calculateBlockProbsMB(wt)
            self.wtsLastBlockProbMBComputation = list(wt)

    def __calculateBlockProbsMB(self, wt):
        self.blockProbsMB = [self._getBlockProbMB(i, wt) for i in xrange(len(self.mrf.pllBlocks))]
    
    def _f(self, wt):
        self._calculateBlockProbsMB(wt)
        print "likelihood calculation..."
        probs = []
        for idxVar in xrange(len(self.mrf.pllBlocks)):
            if self._isQueryVar(idxVar):
                p = self.blockProbsMB[idxVar][self.evidenceIndices[idxVar]]
                if p == 0: p = 1e-10 # prevent 0 probabilities
                probs.append(p)
        return fsum(map(log, probs))
   
    def _grad(self, wt):
        self._calculateBlockProbsMB(wt)
        grad = numpy.zeros(len(self.mrf.formulas), numpy.float64)        
        print "gradient calculation..."
        for idxFormula, d in self.fcounts.iteritems():
            for idxVar, counts in d.iteritems():
                if self._isQueryVar(idxVar):
                    v = counts[self.evidenceIndices[idxVar]]
                    for i in xrange(len(counts)):
                        v -= counts[i] * self.blockProbsMB[idxVar][i]
                    grad[idxFormula] += v
        #print "wts =", wt
        self.grad_opt_norm = float(sqrt(fsum(map(lambda x: x * x, grad))))
        print "grad =", grad, "norm=", self.grad_opt_norm
        return numpy.array(grad)
    
    def _computeStatistics(self):
        '''
        computes the statistics upon which the optimization is based
        '''
        debug = False
        print "computing statistics..."
        
        # get evidence indices
        self.evidenceIndices = []
        for (idxGA, block) in self.mrf.pllBlocks:
            if idxGA is not None:
                self.evidenceIndices.append(0) # 0 = value unchanged, 1 = inverted
            else:
                # find out which ga is true in the block
                idxValueTrueone = -1
                for idxValue, idxGA in enumerate(block):
                    if self.mrf._getEvidence(idxGA):
                        if idxValueTrueone != -1: raise Exception("More than one true ground atom in block '%s'!" % self.mrf._strBlock(block))
                        idxValueTrueone = idxValue
                if idxValueTrueone == -1: raise Exception("No true ground atom in block '%s'!" % self.mrf._strBlock(block))
                self.evidenceIndices.append(idxValueTrueone)
        
        # compute actual statistics
        self.fcounts = {}        
        self.blockRelevantFormulas = defaultdict(set) # maps from variable/pllBlock index to a list of relevant formula indices

        for idxGndFormula, gndFormula in enumerate(self.mrf.iterGroundFormulas(verbose=True)):
            if debug:
                print "  ground formula %d/%d: %s\r" % (idxGndFormula, len(self.mrf.gndFormulas), str(gndFormula))
            
            # get the set of block indices that the variables appearing in the formula correspond to
            idxBlocks = set()
            for idxGA in gndFormula.idxGroundAtoms():
                #if debug: print "    ", self.mrf.gndAtomsByIdx[idxGA]
                idxBlocks.add(self.mrf.atom2BlockIdx[idxGA])
            
            for idxVar in idxBlocks:
                
                if not self._isQueryVar(idxVar):
                    continue
                
                (idxGA, block) = self.mrf.pllBlocks[idxVar]
                
            
                if idxGA is not None: # ground atom is the variable as it's not in a block
                    if debug: print "    ", self.mrf.gndAtomsByIdx[idxGA]

                    # check if formula is true if gnd atom maintains its truth value
                    if self.mrf._isTrueGndFormulaGivenEvidence(gndFormula):
                        self._addMBCount(idxVar, 2, 0, gndFormula.idxFormula)
                        if debug: print "      add 0"

                    # check if formula is true if gnd atom's truth value is inverted
                    old_tv = self.mrf._getEvidence(idxGA)
                    self.mrf._setTemporaryEvidence(idxGA, not old_tv)
                    if self.mrf._isTrueGndFormulaGivenEvidence(gndFormula):
                        self._addMBCount(idxVar, 2, 1, gndFormula.idxFormula)
                        if debug: print "      add 1"
                    self.mrf._removeTemporaryEvidence()
                        
                else: # the block is the variable (idxGA is None)

                    size = len(block)
                    idxGATrueone = block[self.evidenceIndices[idxVar]]
                    
                    # check true groundings for each block assigment
                    for idxValue, idxGA in enumerate(block):
                        if idxGA != idxGATrueone:
                            self.mrf._setTemporaryEvidence(idxGATrueone, False)
                            self.mrf._setTemporaryEvidence(idxGA, True)                            
                        if self.mrf._isTrueGndFormulaGivenEvidence(gndFormula):
                            self._addMBCount(idxVar, size, idxValue, gndFormula.idxFormula)
                        self.mrf._removeTemporaryEvidence()


class DBPLL(BPLL):
    '''
    Specialisation of BPLL for discriminative learning.
    '''    
    
    def __init__(self, mrf, queryPreds=None, **params):
        BPLL.__init__(self, mrf, **params)
        self.queryPreds = queryPreds

    def _isQueryVar(self, idxVar):
        idxGA, block = self.mrf.pllBlocks[idxVar]
        if idxGA is not None:
            predName = self.mrf.gndAtomsByIdx[idxGA].predName 
        else:
            predName = self.mrf.gndAtomsByIdx[block[0]].predName
        return predName in self.queryPreds


class DPLL_ISE_ME(SoftEvidenceLearner, DBPLL):
    '''
    Discriminative pseudologlikelihood learning with independent soft evidence.
    This is a more memory-efficient implementation, which is based on DBPLL, but it 
    does *not* support block variables at all.
    '''
    
    def __init__(self, mrf, queryPreds=None, **params):
        SoftEvidenceLearner.__init__(self, mrf, **params)
        DBPLL.__init__(self, mrf, queryPreds=queryPreds, **params)
        
    def _computeStatistics(self):
        '''
        computes the statistics upon which the optimization is based
        '''
        debug = False
        print "computing statistics..."

        # get evidence indices
        self.evidenceIndices = []
        for (idxGA, block) in self.mrf.pllBlocks:
            if idxGA is not None:
                self.evidenceIndices.append(0) # 0 = value unchanged, 1 = inverted
            else:
                # find out which ga is true in the block
                idxValueTrueone = -1
                for idxValue, idxGA in enumerate(block):
                    if self.mrf._getEvidence(idxGA):
                        if idxValueTrueone != -1: raise Exception("More than one true ground atom in block '%s'!" % self.mrf._strBlock(block))
                        idxValueTrueone = idxValue
                if idxValueTrueone == -1: raise Exception("No true ground atom in block '%s'!" % self.mrf._strBlock(block))
                self.evidenceIndices.append(idxValueTrueone)
        
        # compute actual statistics
        self.fcounts = {}        
        self.blockRelevantFormulas = defaultdict(set) # maps from variable/pllBlock index to a list of relevant formula indices

        for idxGndFormula, gndFormula in enumerate(self.mrf.iterGroundFormulas(verbose=True)):
            if debug:
                print "  ground formula %d/%d: %s\r" % (idxGndFormula, len(self.mrf.gndFormulas), str(gndFormula))
            
            # get the set of block indices that the variables appearing in the formula correspond to
            idxBlocks = set()
            for idxGA in gndFormula.idxGroundAtoms():
                #if debug: print "    ", self.mrf.gndAtomsByIdx[idxGA]
                idxBlocks.add(self.mrf.atom2BlockIdx[idxGA])
            
            for idxVar in idxBlocks:
                
                if not self._isQueryVar(idxVar):
                    continue
                
                (idxGA, block) = self.mrf.pllBlocks[idxVar]
                
            
                if idxGA is not None: # ground atom is the variable as it's not in a block
                    if debug: print "    ", self.mrf.gndAtomsByIdx[idxGA]

                    ga = self.mrf.gndAtomsByIdx[idxGA]
                    old_tv = self.mrf._getEvidenceDegree(ga)
                    
                    tg1 = self._getTruthDegreeGivenEvidence(gndFormula)
                    #print "%s: %f (%f)" % (gndFormula, tg1, old_tv)
                    if tg1 > 0: self._addMBCount(idxVar, 2, 0, gndFormula.idxFormula, increment=tg1)
                    
                    self.mrf._setSoftEvidence(ga, 1 - old_tv)
                    tg2 = self._getTruthDegreeGivenEvidence(gndFormula)
                    if tg2 > 0: self._addMBCount(idxVar, 2, 1, gndFormula.idxFormula, increment=tg2)
                    self.mrf._setSoftEvidence(ga, old_tv)

                else: # the block is the variable (idxGA is None)

                    raise Exception("Block variables are not supported by this learner")
        

class BPLL_CG(BPLL):
    '''
        BPLL learner variant that uses a custom grounding procedure to increase
        efficiency.
    '''
    
    groundingMethod = 'BPLLGroundingFactory'
    
    def __init__(self, mrf, **params):
        BPLL.__init__(self, mrf, **params)
    
    def _prepareOpt(self):
        print "constructing blocks..."
        self.mrf._getPllBlocks()
        self.mrf._getAtom2BlockIdx()
        self.fcounts = self.mrf.groundingMethod.fcounts
        self.blockRelevantFormulas = self.mrf.groundingMethod.blockRelevantFormulas
        self.evidenceIndices = self.mrf.groundingMethod.evidenceIndices
