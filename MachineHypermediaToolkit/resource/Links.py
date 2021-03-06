

class Links(object) :
    
    def __init__(self, links=None) :
        """initialize with a set of links default to none"""
        self._links = []
        if None != links:
            self.add(links)
            
    def add(self, links) :
        """links contains a map or array of maps in link-format"""
        if isinstance(links, list) :
            self._links.extend(links)
        else :
            self._links.append(links)

    def get(self, selectMap=None) :
        if selectMap == None or len(selectMap) == 0:
            return(self._links)
        else:
            self._result = []
            for index in self.select(selectMap) :
                self._result.append(self._links[index])
            return self._result
    
    def selectMerge(self, selectMap, mergeMap) :
        """patch contains a selection map and merge map in JSON merge-patch format"""
        self._linkList = self.select(selectMap)
        if len(self._linkList) == 0:
            self.add(mergeMap)
        else:
            # reverse the list so multiple deletions don't change the index of earlier elements
            self._linkList.reverse()
            for self._index in self._linkList :
                if mergeMap == {} :
                    del self._links[self._index]
                else:
                    for attribute in mergeMap:
                        if mergeMap[attribute] == None: 
                            del self._links[self._index][attribute]
                        elif attribute not in self._links[self._index]:
                            self._links[self._index][attribute] = mergeMap[attribute]
                        else:
                            # merge attributes between lists and string values
                            if isinstance(self._links[self._index][attribute], list):
                                if isinstance(mergeMap[attribute], list) :
                                    # adding a list to a list, factor out duplicates
                                    self._links[self._index][attribute].extend( \
                                    [ attr for attr in mergeMap[attribute] \
                                    if attr not in self._links[self._index][attribute] ] )
                                elif mergeMap[attribute] not in self._links[self._index][attribute] :
                                    self._links[self._index][attribute].append(mergeMap[attribute])
                            else:
                                if isinstance(mergeMap[attribute], list) :
                                    # adding a list to a string results in a list
                                    if self._links[self._index][attribute] in mergeMap[attribute] :
                                        self._links[self._index][attribute] = mergeMap[attribute]
                                    else:
                                        self._links[self._index][attribute] = \
                                        [self._links[self._index][attribute]].extend(mergeMap[attribute])
                                else:
                                    # adding a string to a string results in a list
                                    if mergeMap[attribute] != self._links[self._index][attribute]:
                                        self._links[self._index][attribute] = \
                                        [self._links[self._index][attribute], mergeMap[attribute]]
       
    def select(self, selectMap) :
        """selectMap contains a selection map in query filter format"""
        """returns a list of indices to getLinks in the link array that match the query filter"""
        self._selection = []
        """check all getLinks in the collection"""
        for self._linkIndex in range(0, len(self._links)) :
            self._selected = True
            """test each attribute in the selectMap"""
            for attribute in selectMap :
                if attribute not in self._links[self._linkIndex] :
                    self._selected = False
                    break
                if isinstance(selectMap[attribute], list) :
                    """multi value attributes in selectMap, all values must be present to select """
                    for self._attr_val in selectMap[attribute]:
                        if isinstance(self._links[self._linkIndex][attribute], list) :
                            """multi value attribute in link"""
                            if self._attr_val not in self._links[self._linkIndex][attribute] :
                                self._selected = False
                                break
                        elif self._attr_val != self._links[self._linkIndex][attribute] :
                            """single value attribute in link"""
                            self._selected = False
                            break
                elif isinstance(self._links[self._linkIndex][attribute], list):
                    """single value attribute in selectMap, multi value in link"""
                    if selectMap[attribute] not in self._links[self._linkIndex][attribute] :
                        self._selected = False
                        break
                elif selectMap[attribute] != self._links[self._linkIndex][attribute] :
                    """single value in both selectMap and link"""
                    self._selected = False
                    break
            if self._selected :
                self._selection.append(self._linkIndex)
            
        return self._selection

