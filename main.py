import cacheUtils as cu
import random


def nominalSizeConvert(size):
  head = size.rstrip('ABCDEFGHIJKLMNOPQRSTUVWXYZ ').strip()
  tail = size[len(head):].strip()
  num = int(head)
  if tail == "KB":
    return num * (2**10)
  elif tail == "MB":
    return num * (2**20)
  elif tail == "GB":
    return num * (2**30)
  elif tail == "TB":
    return num * (2**40)
  else:
    return num

def main():
  print("Cache Memory Simulator")

  # PROMPT FOR CACHE PARAMETERS
  sizeIn = input("Enter the Nominal Size of the cache in bytes: ")
  Words_Per_Block = input("Enter the number of words per block (1,2,4,8): ")
  MPin = input("Enter the Mapping Policy (DM,SA): ")

  # Check for Set associative --> prompt for other parameters
  if MPin.lower() in ["sa", "s a", "setassociative", "set associative"]:
    Blocks_Per_Set = input("Enter the number of blocks per set: ")
    MP = cu.mappingPolicy.SA
    RPin = input("Enter the replacement policy (LRU/Random): ")
    if (RPin.lower() in ["lru", "l r u", "leastrecentlyused", "least recently used"]):
      RP = cu.replacementPolicy.LRU
    elif (RPin.lower() in ["random", "rand", "r"]):
      RP = cu.replacementPolicy.RANDOM
    else:
      print("Input not recognized. Valid inputs are (LRU, Random)")
      exit()
  elif (MPin.lower() in ["dm", "d m", "directmapped", "direct mapped"]):
    Blocks_Per_Set = 1
    RP = cu.replacementPolicy.NULL
    MP = cu.mappingPolicy.DIRECT
  else:
    print("Input not recognized. Valid inputs are (DM, SA)")
    exit()

  size = int(nominalSizeConvert(sizeIn))
  Bytes_Per_Block = int(Words_Per_Block) * 4

  # CREATE CACHE
  cache = cu.Cache(size, int(Words_Per_Block), MP, int(Blocks_Per_Set), RP)
  
  # PRINT DATA
  print("The cache nominal size is: " + str(cache.nominalSize) + " bytes")
  print("The mapping policy is: " + cache.mP.name)
  print("The number of blocks in the cache is: " + str(cache.numBlocks) + " blocks")
  print("The number of words per block is: " + str(cache.wordsPerBlock))
  if MP == cu.mappingPolicy.SA:
    print("The number of sets in the cache is: " + str(cache.numSets) + " sets")
    print("The number of blocks per set is: " + str(cache.blocksPerSet))
    print("The replacement policy is: " + cache.rP.name)
  print("The number of index bits is: " + str(cache.indexBits))
  print("The number of offset bits is: " + str(cache.offsetBits))
  print("The number of status bits is: " + str(cache.statusBits))
  print("The number of tag bits is: " + str(cache.tagBits))
  print("The real cache size is: " + str(cache.realSize) + " bytes")
  
  # Choose Operating Mode
  while (True):
    OpMode = input("Select an operating mode (Default/Sim/End): ")
    if OpMode.lower() == "end":
      break
    else:
      if OpMode.lower() == "default":
        #Default Mode
        while True:
          DefaultIn = input("Enter the word address,  'clear', or 'exit': ")
          if DefaultIn.lower() == "exit":
            break
          elif DefaultIn.lower() == "clear":
            cache.clear()
          else:
            Word_address_int = int(DefaultIn)
            hitStatus = cache.access(Word_address_int)
            print("Cache access of " + str(Word_address_int) + " was a " + hitStatus.name)
          cache.print()
      if OpMode.lower() == "sim":
        while True:
          SimIn = input("Enter 'begin', 'clear', or 'exit': ")
          if SimIn.lower() == "exit":
            break
          elif SimIn.lower() == "clear":
            cache.clear()
            cache.print()
          else:
            # SIMULATION MODE
            # CREATE RANDOM ACCESSES
            Accesses = []
            Accesses.append(random.randint(0, cache.nominalSize))
            NumAccess = input("Enter the number of accesses: ")
            Locality = float(input("Enter the locality (%): "))
            for i in range(int(NumAccess) - 1):
              isLocal = random.random()
              if isLocal < Locality:
                Accesses.append(Accesses[i - 1])
              else:
                Accesses.append(random.randint(0, cache.nominalSize))
            # SIMULATE CACHE
            cache.print()
            hits = 0
            for access in Accesses:
              # State which address is being accessed
              # Access Cache
              # Track hits & misses
              # report hit rate & miss rate
              print("accessing" + " " + str(access))
              hits += cache.access(access).value
            hitrate=hits*100//int(NumAccess)
            missrate=100-hitrate
            print("")
            cache.print()
            print("")
            print("hits:",str(hits))
            print("misses:",str(int(NumAccess)-hits))
            print("hitrate:",str(hitrate),"%")
            print("missrate:",str(missrate),"%")

if __name__ == "__main__":
  main()
