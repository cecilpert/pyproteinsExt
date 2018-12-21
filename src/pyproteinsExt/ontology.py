# This package provides utility function to manipulate the GO/MI ontology terms
# check performed on passed string is a bit clunky
# "obo:MI_0090" or "MI:0090" are OK
import re
import ontospy as on

def isOboRegular(term):
   # print "Coucou " + term
  #  print re.match(r'^obo:[A-Z]{2}:[0-9]{4}$', term)
    return re.match(r'^obo:[A-Z]{2}_[0-9]{4}$', term)#


# Manipulating the MolecularInteraciton ontology
#print model.classes
#aClass = model.getClass("MI_0090")
#aClass[0].children()
#model.printClassTree()


class Ontology(on.Ontospy):
    def __init__(self, ressource):
        super(Ontology, self).__init__(ressource)

    def find(self, stringTerm):
        if isOboRegular(stringTerm):
            u = stringTerm
        else:
            u = stringTerm.replace(":", "_")
        return self.getClass(u)

    def findOne(self, stringTerm):
       x = self.find(stringTerm)
       if x:
        return x[0]

        return None

    # if term is a string coherce it in a ontology class object
    def _coherce(self, data):
        if not isinstance(data, list):
            data = [data]
        return [ self._termCoherce(e) for e in data ]

    def _termCoherce(self, termLike):
        if isinstance(termLike, str):
            term = self.findOne(termLike)
            if not term:
                raise ValueError("No such term found : \"" + str(termLike) + "\"")
            termLike = term

        return termLike

# Find and Count foreach provided term in
# the correesponding parents in range domain the number
    def project(self, domainTerms, rangeTerms, flatDic=False):

        domainTerms = self._coherce(domainTerms)
        res = { x : [] for x in self._coherce(rangeTerms) }
        others = []
        for query in domainTerms:
            known = False
            for rangeTerm in res:
                if self.isSonOf(query, rangeTerm):
                    res[rangeTerm].append(query)
                    known = True
            if not known:
                others.append(query)

        if not flatDic:
            res["others"] = others
            return res

        data = { "term" : [], "parent" : [] }
        for rangeTerm in res:
            for son in res[rangeTerm]:
                data["term"].append( str(son.bestLabel()) )
                data["parent"].append( str(rangeTerm.bestLabel()) )
        for query in others:
            data["term"].append( str(query.bestLabel()) )
            data["parent"].append( "others" )

        return data
        #results = {  for }


    def isSonOf(self, x, y):
        x, y = self._coherce([x, y])
        return y in self._getLineage(x)


    def _getLineage(self, term):
        term = self._coherce(term)[0]

        lineage = []

        tmpNode = self._rollupNode(term)
        if not tmpNode:
            print str(term) + ' has no parent'

        while tmpNode:
            lineage.append(tmpNode)
            tmpNode = self._rollupNode(tmpNode)

        return lineage

    def _rollupNode(self, e):
        if not e.parents():
            return None
        return e.parents()[0]
