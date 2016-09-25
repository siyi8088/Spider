import numpy
nwalks=5000
nsteps=1000
draws=numpy.random.normal(loc=0,scale=0.25,size=(nwalks,nsteps))
steps=numpy.where(draws>0,1,-1)
walks=steps.cumsum(1)
hits30=(numpy.abs(walks)>=30).any(1)
hits30.sum()

crossing_times=(numpy.where(draws[hits30])>=30).argmax(1)
crossing_times.mean()
