from enum import Enum
import math
import random


class replacementPolicy(Enum):
  NULL = 0
  RANDOM = 1
  LRU = 2


class mappingPolicy(Enum):
  NULL = 0
  DIRECT = 1
  SA = 2


class hitStatus(Enum):
  MISS = 0
  HIT = 1


# Class representing the cache
# Contains some information about the cache parameters, as well as an array
# of Sets, each of which contains an array of blocks
class Cache:
  nominalSize = 0
  mP = mappingPolicy.NULL
  numBlocks = 0
  wordsPerBlock = 0
  bytesPerBlock = 0
  numSets = 0
  blocksPerSet = 0
  rP = replacementPolicy.NULL
  indexBits = 0
  offsetBits = 0
  statusBits = 0
  tagBits = 0
  realSize = 0
  Sets = []

  def __init__(self, nominalSize, wordsPerBlock, mP, blocksPerSet, rP):
    self.nominalSize = nominalSize
    self.wordsPerBlock = wordsPerBlock
    self.mP = mP
    self.blocksPerSet = blocksPerSet
    self.rP = rP
    self.bytesPerBlock = wordsPerBlock * 4
    self.numBlocks = nominalSize // (self.bytesPerBlock)
    self.numSets = (self.numBlocks) // blocksPerSet
    self.indexBits = math.ceil(math.log2(self.numSets))
    self.offsetBits = math.ceil(math.log2(self.bytesPerBlock))
    if mP == mappingPolicy.DIRECT:
      self.statusBits = 1
    else:
      self.statusBits = 1 + blocksPerSet
    self.tagBits = 32 - self.indexBits - self.offsetBits
    self.realSize = nominalSize + (self.numBlocks *
                                   (self.statusBits + self.tagBits)) * 4 // 32
    self.Sets = [
        Set(blocksPerSet, wordsPerBlock, 0, rP, self.numSets, empty=1)
        for i in range(self.numSets)
    ]

  def access(self, wordAddr):
    blockAddr = wordAddr // self.wordsPerBlock
    setAddr = blockAddr % self.numSets
    if self.Sets[setAddr].empty:
      #Set is empty; add block; return miss
      self.Sets[setAddr].addBlock(blockAddr)
      return hitStatus.MISS
    else:
      #Set contains at least 1 block; check for hit
      return self.Sets[setAddr].access(blockAddr)

  def print(self):
    if(self.numSets > 32):
      print("Cache too large to print.")
    else:
      print("Current cache status:")
      for i in range(self.numSets):
        if self.Sets[i].empty == 0:
          print(str(i) + ": ", end=" ")
          self.Sets[i].print()
        else:
          print(str(i) + ":")

  def clear(self):
    self.Sets = [
        Set(self.blocksPerSet,
            self.wordsPerBlock,
            0,
            self.rP,
            self.numSets,
            empty=1) for i in range(self.numSets)
    ]


# Class representing a Set
# Contains some information about the Set parameters, as well as an array
# of Blocks, each of which contains an array of words
class Set:

  def __init__(self,
               blocksPerSet,
               wordsPerBlock,
               blockAddr,
               rP,
               numSets,
               empty=0):
    self.Blocks = []
    self.empty = empty
    self.blocksPerSet = blocksPerSet
    self.wordsPerBlock = wordsPerBlock
    self.setAddr = blockAddr % numSets
    self.numSets = numSets
    self.rP = rP

  def access(self, blockAddr):
    #Check for hit
    for block in self.Blocks:
      if block.blockAddr == blockAddr:
        #hit!
        if self.rP == replacementPolicy.LRU:
          #Set associative, LRU rp; set LRU bits
          #increment counters of all but accessed block
          for block2 in self.Blocks:
            if block2 != block:
              block2.incrementCounter()
        #Direct Mapped or Set Associative Random rp
        return hitStatus.HIT

    #miss :(
    if self.rP == mappingPolicy.NULL:
      #Direct Mapped; erase block; add new; return miss
      self.Blocks.clear()
    elif not self.isFull():
      #Set Associative, non-full set
      if self.rP == replacementPolicy.LRU:
        #increment blocks counter, add new, return miss
        for block in self.Blocks:
          block.incrementCounter()
      #else Random, non-full set; add new, return miss
    else:
      #Set associative, set is full
      if self.rP == replacementPolicy.LRU:
        #LRU, erase lru block, add new, return miss
        self.eraseLRU()
      else:
        #Random, erase random block, add new, return miss
        self.eraseRandom()
    self.addBlock(blockAddr)
    return hitStatus.MISS

  def isFull(self):
    return len(self.Blocks) == self.blocksPerSet

  def eraseLRU(self):
    #Find LRU block
    #Counters will be unique, so loop through all
    # and save highest.
    highestCounter = 0
    for block in self.Blocks:
      if block.accessedCounter > highestCounter:
        highestCounter = block.accessedCounter
    #Erase it
    for block in self.Blocks:
      if block.accessedCounter == highestCounter:
        self.Blocks.remove(block)
        break

  def eraseRandom(self):
    index = random.randint(0, self.blocksPerSet - 1)
    self.Blocks.pop(index)

  def addBlock(self, blockAddr):
    self.Blocks.append(Block(self.wordsPerBlock, blockAddr))
    self.setAddr = blockAddr % self.numSets
    self.empty = 0

  def print(self):
    if self.empty != 1:
      if self.rP != replacementPolicy.NULL:
        print("S" + str(self.setAddr) + "[", end=" ")
      for block in self.Blocks:
        block.print()
      if self.rP != replacementPolicy.NULL:
        print("]")
      else:
        print("")


# Class representing a Block
# Contains some information about the block parameters, as well as an array
# of word addresses, and an integer representing the order of block accesses
# in the set
class Block:

  def __init__(self, wordsPerBlock, blockAddress):
    self.wordsPerBlock = wordsPerBlock
    self.accessedCounter = 0
    self.blockAddr = blockAddress
    self.wordAddrs = []
    for i in range(wordsPerBlock):
      self.wordAddrs.append(self.blockAddr * wordsPerBlock + i)

  def print(self):
    print("B" + str(self.blockAddr) + "[", end=" ")
    for i in range(self.wordsPerBlock):
      print("w" + str(self.wordAddrs[i]), end=" ")
      if (i != self.wordsPerBlock - 1):
        print(",", end=" ")
    print("]", end=" ")

  def incrementCounter(self):
    self.accessedCounter += 1
