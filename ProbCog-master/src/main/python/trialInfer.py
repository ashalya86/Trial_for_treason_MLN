from mlnQueryTool import MLNInfer

inf = MLNInfer()
# mlnFiles = ["smoking.mln"]
# db = "smokingDB.db"
mlnFiles = ["trial27.mln"]
db = "trial21.db"

# queries = "cooperate(Skolem, SecureCity) ^ convicted(Leocrates), convicted(Leocrates), cooperate(Skolem, SecureCity) ^ !convicted(Leocrates), !convicted(Leocrates)"
queries = "cooperate(Polites, SecureCity)"
# queries = "Cancer"
# queries = " individual_ethos(x, Ethos2) ^ cooperate(x, SecureCity)"
# queries = "individual_ethos(x, Ethos1) ^ cooperate(x, SecureCity)"
output_filename = "results.txt"
allResults = {}
tasks = (("exact inference", "PyMLNs"), ("MC-SAT", "J-MLNs"))
# tasks = (("MC-SAT", "PyMLNs"), ("MC-SAT", "J-MLNs"))
for method, engine in tasks[:-1]:
    allResults[(method, engine)] = inf.run(
        mlnFiles,
        db,
        method,
        queries,
        engine,
        output_filename,
        saveResults=True,
        maxSteps=100,
    )

for (method, engine), results in allResults.iteritems():
    print("Results obtained using %s and %s" % (engine, method))
    for atom, p in results.iteritems():
        print("  %.6f  %s" % (p, atom))
