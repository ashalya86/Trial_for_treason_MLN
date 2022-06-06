from optparse import Values
import MLN
from MLN.inference import ExactInference
from mlnQueryTool import MLNInfer

print("Hello")
inf = MLNInfer()
mlnFiles = ["smoking.mln"]
db = "smokingDB.db"
queries = "cooperate(Skolem, SecureCity), individual_ethos(Skolem,Ethos1), individual_ethos(Skolem,Ethos2)"

# create MLN
verbose = True
mln = MLN.MLN(
    mlnFiles,
    verbose=verbose,
    defaultInferenceMethod=MLN.InferenceMethods.byName("exact inference"),
)
# print(mln.domains)
print("param", mln.parameterType)
infer = ExactInference(mln)
infer._infer()
# print(infer._infer())
# mrf = MLN.MRF(mln, db, verbose=False,)
# poss = mrf._createPossibleWorlds()
# mrf.printTopWorlds(10,1,1)
# print(poss)
# print(mrf.getWorld(2))
# inf = ExactInference(mln)
# inf._infer()
