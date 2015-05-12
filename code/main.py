import numpy as np
import matplotlib.pyplot as plt
from noisy_plane import generate_samples, lnlike, lnlikeH, lnlikeHM
from model import model1, model
import emcee
import triangle
import sys
import h5py

def lnprior(pars):
    m, c, sig, Y, V, P = pars
    if 0. < P < 1. and 0. < V:
        return 0.
    return -np.inf

def lnprob(pars, samples, obs, u):
    return lnlikeHM(pars, samples, obs, u) + lnprior(pars)

def MCMC(whichx, nsamp):

    # set initial params. slope, intercept, sigma, Y, V, P
    rho_pars = [-2., 6., .0065, -.5, .5, .1]
    logg_pars = [-1.850, 7., .0065, 4., 1., .1]
    pars_init = logg_pars
    if whichx == "rho":
        pars_init = rho_pars

    # load data
    fr, frerr, r, rerr = np.genfromtxt("../data/flickers.dat").T
    fl, flerr, l, lerr, t, terr = np.genfromtxt("../data/log.dat").T
    nd = 20
    x, xerr, y, yerr = fl[:nd], flerr[:nd], l[:nd], lerr[:nd]
    if whichx == "rho":
        x, xerr, y, yerr = fr[:nd], frerr[:nd], r[:nd], rerr[:nd]

    # format data and generate samples
    obs = np.vstack((x, y))
    u = np.vstack((xerr, yerr))
    s = generate_samples(obs, u, nsamp)

    # set up and run emcee
    ndim, nwalkers = len(pars_init), 32
    pos = [pars_init + 1e-4*np.random.randn(ndim) for i in range(nwalkers)]
    sampler = emcee.EnsembleSampler(nwalkers, ndim, lnprob,
                                    args=(s, obs, u))
    print "burning in..."
    pos, _, _, = sampler.run_mcmc(pos, 500)
    sampler.reset()
    print "production run..."
    sampler.run_mcmc(pos, 1000)
    samp = sampler.chain[:, 50:, :].reshape((-1, ndim))
    m, c, sig, Y, V, P, = map(lambda v: (v[1], v[2]-v[1], v[1]-v[0]),
               zip(*np.percentile(samp, [16, 50, 84], axis=0)))
    pars = [m[0], c[0], sig[0]]

    # save samples
    print np.shape(samp)
    f = h5py.File("%s_samples.h5" % whichx, "w")
    data = f.create_dataset("samples", np.shape(samp))
    data[:, 0] = samp[:, 0]
    data[:, 1] = samp[:, 1]
    data[:, 2] = samp[:, 2]
    data[:, 3] = samp[:, 3]
    data[:, 4] = samp[:, 4]
    data[:, 5] = samp[:, 5]
    f.close()

def make_plots(whichx):

    # load data
    fr, frerr, r, rerr = np.genfromtxt("../data/flickers.dat").T
    fl, flerr, l, lerr, t, terr = np.genfromtxt("../data/log.dat").T
    nd = 20
    x, xerr, y, yerr = fl[:nd], flerr[:nd], l[:nd], lerr[:nd]
    if whichx == "rho":
        x, xerr, y, yerr = fr[:nd], frerr[:nd], r[:nd], rerr[:nd]

    with h5py.File("%s_samples.h5" % whichx) as f:
        samp = f["samples"][...]
    m, c, sig, Y, V, P = map(lambda v: (v[1], v[2]-v[1], v[1]-v[0]),
               zip(*np.percentile(samp, [16, 50, 84], axis=0)))
    pars = [m[0], c[0], sig[0]]

    plt.clf()
    plt.errorbar(x, y, xerr=xerr, yerr=yerr, fmt="k.", capsize=0, ecolor=".7")
    plt.plot(x, model1(pars, x), "k")
    ndraws = 100
    p1s = np.random.choice(samp[:, 0], ndraws)
    p2s = np.random.choice(samp[:, 1], ndraws)
    for i in range(ndraws):
        plt.plot(x, model1([p1s[i], p2s[i]], x), "k", alpha=.1)
    plt.savefig("mcmc_%s" % whichx)
    labels = ["$m$", "$c$", "$\sigma$", "$Y$", "$V$", "$f$"]
    fig = triangle.corner(samp, labels=labels)
    fig.savefig("triangle_%s" % whichx)

if __name__ == "__main__":
    whichx = str(sys.argv[1])
#     MCMC(whichx, 50)
    make_plots(whichx)
