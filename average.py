#!/usr/bin/python3

import pyBigWig
from pathos.multiprocessing import ProcessingPool 
import sys, getopt

def minCoverage(bw, chroms):
    return(min([bw.stats(i, type="coverage") for i in chroms]))


def avgTrack(file, chrom, size, chromsize):
    with pyBigWig.open(file) as bw:
        avg = [bw.stats(chrom, i * size, (i + 1) * size)[0] for i in range(int(chromsize / size))]
        return([chrom, avg])

def delNone(l):
    while l[len(l) - 1] == None:
        l = l[:-1]
    return(l)

if __name__ == "__main__":    
    chroms = ["chr" + str(i + 1) for i in range(22)] + ["chrX", "chrY"]
    file, size, outfile = None, None, None
    opts, args = getopt.getopt(sys.argv[1:], "hi:o:s:")
    for opt, arg in opts:
        if opt == '-h':
            print('average.py -i <inputfile> -o <outputfile> -s <windowsize>')
            sys.exit()
        elif opt == "-i":
            file = arg
        elif opt == "-o":
            outfile = arg
        elif opt == "-s":
            size = int(arg)
    if None in (file, size, outfile):
        print('average.py -i <inputfile> -o <outputfile> -s <windowsize>')
        sys.exit(2)            

    with pyBigWig.open(file) as bw:
        #print("Mimimum coverage:" + str(minCoverage(bw, chroms)))
        header = {key:value for key, value in bw.chroms().items() if key in chroms}
    p = ProcessingPool(nodes=8)
    avgs = p.map(lambda chrom: avgTrack(file, chrom, size, header[chrom]), chroms)
    avg = {i[0]:i[1] for i in avgs}
    with pyBigWig.open(outfile, "w") as bw:
        bw.addHeader([(i, header[i]) for i in chroms])
        for i in chroms:
#            bw.addEntries(i, 0, values=[k for k in avg[i] if type(k) == float], span=size, step=size)
            bw.addEntries(i, 0, values=delNone(avg[i]), span=size, step=size)
