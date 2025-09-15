#
def wrtcfg(fln, *migr):
  tlen = len(migr)
  str0 = ['0']*tlen
  with open(fln, 'w') as f:
    for ii in range(0, tlen):
      for jj in range(0, tlen):
        if ii==jj:continue
        str1 = str0[:]
        str1[jj:jj+1] = '%d'%1
        f.write('<parameter id="%2s-to-%2s" value="\n'%(migr[ii], migr[jj]))
        for kk in range(0, ii):
           f.write(' '.join(str0)+'\n')
        f.write(' '.join(str1)+'\n')
        for kk in range(ii+1, tlen):
           f.write(' '.join(str0)+'\n')
        f.write('"/>\n')

