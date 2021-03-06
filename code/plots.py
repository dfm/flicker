import numpy as np
import matplotlib.pyplot as plt
import triangle
import scipy.interpolate as spi
import h5py
import sys
from noisy_plane import model1
from model import load_data

def interp(xold, yold, xnew, s):
    tck = spi.splrep(xold, yold, s=s)
    ynew = spi.splev(xnew, tck, der=0)
    return ynew

def fit_straight_line(x, y, yerr):
    AT = np.vstack((np.ones_like(x), x))
    C = np.eye(len(y)) * yerr**2
    ATCA = np.dot(np.dot(AT, C), AT.T)
    ATCy = np.dot(np.dot(AT, C), y)
    return np.linalg.solve(ATCA, ATCy)

def make_inverse_flicker_plot(x, xerr, y, yerr, samples, whichx, ndraws,
                              plot_samp=False, fractional=True):

    # fit straight line
    lim = 200
    a1 = fit_straight_line(x[:lim], y[:lim], yerr[:lim])
    a2 = fit_straight_line(x[lim:], y[lim:], yerr[lim:])

    assert np.shape(samples)[0] < np.shape(samples)[1], \
            "samples is wrong shape"
    beta, alpha, tau = np.median(samples, axis=1)
    sigma = (np.sqrt(abs(tau)))
    pars = [beta, alpha, sigma]

    print alpha, beta, tau, sigma
    ys = alpha + beta * x
    sig_tot = sigma + yerr
    ys = np.linspace(min(y)-5, max(y)+5, 1000)
    xs = np.linspace(1., 2.4, 100)
    plt.clf()

    b_samp = np.random.choice(samples[0, :], ndraws)
    a_samp = np.random.choice(samples[1, :], ndraws)
    s_samp = np.random.choice(samples[2, :], ndraws) * np.random.randn(ndraws)

    if whichx == "rho":
        plt.ylabel("$\log_{10}(\\rho_{\star}[\mathrm{g~cm}^{-3}])$")
        col = "#FF33CC"
        plt.text(1.55, .5, "$\log_{10} (\\rho_{\star}) \sim \mathcal{N} \
                 (\\alpha + \\beta \log_{10}(F_8), \sigma_{\\rho})$")
        plt.text(1.95, .22, "$\\alpha = %.3f$" % (alpha-3))
        plt.text(1.95, .07, "$\\beta = %.3f$" % beta)
        plt.text(1.95, -.08, "$\\sigma_{\\rho} = %.3f$" % tau**.5)
        plt.ylim(-2, 1)
        for i in range(ndraws):
            ys = model1([b_samp[i], a_samp[i]], xs)
            if fractional:
                plt.plot(xs, ys + ys * s_samp[i], col, alpha=.05)
            else:
                plt.plot(xs, ys + s_samp[i], col, alpha=.05)
        plt.plot(xs, model1(pars, xs)-3, ".2", linewidth=1)
        plt.errorbar(x, y-3, xerr=xerr, yerr=xerr, fmt="k.", capsize=0,
                             alpha=.5, ecolor=".5", mec=".2")
        plt.plot(xs, model1(pars, xs)+sigma-3, "k--")
        plt.plot(xs, model1(pars, xs)-sigma-3, "k--")

    elif whichx == "logg":
        plt.ylim(3, 5)
        col = "#0066CC"
        plt.ylabel("$\log_{10}(g [\mathrm{cm~s}^{-2}])$")
        plt.text(1.6, 4.7, "$\log(g) \sim \mathcal{N} \
                 (\\gamma + \\delta \log_{10}(F_8), \\sigma_g)$")
        plt.text(1.95, 4.52, "$\\gamma = %.3f$" % alpha)
        plt.text(1.95, 4.42, "$\\delta = %.3f$" % beta)
        plt.text(1.95, 4.32, "$\\sigma_g = %.3f$" % tau**.5)
        for i in range(ndraws):
            ys = model1([b_samp[i], a_samp[i]], xs)
            if fractional:
                plt.plot(xs, ys + ys * s_samp[i], col, alpha=.05)
            else:
                plt.plot(xs, ys + s_samp[i], col, alpha=.05)
        plt.plot(xs, model1(pars, xs), ".2", linewidth=1)
        plt.errorbar(x, y, xerr=xerr, yerr=yerr, fmt="k.", capsize=0,
                     alpha=.5, ecolor=".5", mec=".2")
        ys = model1(pars, xs)
        if fractional:
            plt.plot(xs, ys + ys*sigma, "k--")
            plt.plot(xs, ys - ys*sigma, "k--")
        else:
            plt.plot(xs, ys + sigma, "k--")
            plt.plot(xs, ys - sigma, "k--")
#         ys1 = np.linspace(3, y[l], 10)
#         ys2 = np.linspace(y[l], 5, 10)
#         plt.plot(a1[0]+a1[1]*ys1, ys1, "r", linewidth=1)
#         plt.plot(a2[0]+a2[1]*ys2, ys2, "g", linewidth=1)
#         xs1 = np.linspace(1, x[lim], 10)
#         xs2 = np.linspace(x[lim], 2.4, 10)
#         plt.plot(xs1, a1[0] + a1[1]*xs1, "m", linewidth=1)
#         plt.plot(xs2, a2[0] + a2[1]*xs2, "m", linewidth=1)
#         xs = np.linspace(1, 2.5, 100)-3
#         ys = 1.15136-3.59637*xs-1.40002*xs**2-.22993*xs**3
#         plt.plot(xs+3, ys, "c", linewidth=1)

    plt.subplots_adjust(bottom=.1)

    plt.xlim(1, 2.4)
    plt.xlabel("$\log_{10}\mathrm{(F}_8~\mathrm{[ppm]})$")
    print "..figs/%s_vs_flicker.pdf" % whichx
    plt.savefig("../figs/%s_vs_flicker.pdf" % whichx)
    plt.savefig("flicker_inv_%s" % whichx)

    plt.clf()
    plt.ylim(4.6, 3.2)
    x -= 3
    xs = np.linspace(min(x), max(x), 100)
    plt.plot(10**x, y, "ko")
    ys = 1.15136-3.59637*xs-1.40002*xs**2-.22993*xs**3
    plt.plot(10**xs, ys, "m")
    plt.savefig("bastien_figureS2")

def make_flicker_plot(x, xerr, y, yerr, samples, plot_samp=False):

    assert np.shape(samples)[0] < np.shape(samples)[1], \
            "samples is wrong shape"

    alpha, beta, tau = np.median(samples, axis=1)
    sigma = np.sqrt(tau)
    print alpha, beta, tau, sigma

    ys = alpha + beta * x
    sig_tot = sigma + yerr
    xs = np.linspace(1., 2.4, 1000)

    plt.clf()
    # plot posterior samples
    if plot_samp:
        # sample posteriors
        nsamp = 1000
        a = np.random.choice(samples[0, :], nsamp)
        b = np.random.choice(samples[1, :], nsamp)
        t = np.random.choice(samples[2, :], nsamp)
        s = np.sqrt(t)
        for i in range(nsamp):
            plt.plot(xs, a[i]+b[i]*xs+np.random.randn(1)*s[i], color=".5",
                     alpha=.03)
    else:
        # intrinsic scatter
        plt.fill_between(xs, alpha+beta*xs-sigma, alpha+beta*xs+sigma,
                         color=cols.blue, alpha=.4, edgecolor="w")
        plt.fill_between(xs, alpha+beta*xs-2*sigma, alpha+beta*xs+2*sigma,
                         color=cols.blue, alpha=.2, edgecolor="w")

    plt.errorbar(x, y, xerr=xerr, yerr=yerr, fmt="k.", capsize=0, alpha=.5,
                 ecolor=".5", mec=".2")
#     plt.errorbar(xx, yy, xerr=xxerr, yerr=yyerr, fmt="r.", capsize=0, alpha=.5,
#                  ecolor="r")
    plt.plot(xs, alpha+beta*xs, ".2", linewidth=1)

    plt.xlim(min(xs), max(xs))
    plt.ylim(.5, 2.5)
    plt.xlabel("$\log_{10}(\\rho_{star}[\mathrm{kgm}^{-3}])$")
    plt.ylabel("$\log_{10}\mathrm{(8-hour~flicker~[ppm])}$")
    if plot_samp:
        plt.savefig("flicker2")
    else:
        plt.savefig("flicker")

    resids = y - (alpha+beta*x)
    normed_resids = resids / np.sqrt(yerr**2 + sigma**2)
    np.savetxt("normed_resids_%s.txt", np.transpose(normed_resids))
    plt.clf()
    plt.hist(normed_resids, 20, histtype="stepfilled", color="w")
    plt.xlabel("Normalised residuals")
    plt.savefig("residual_hist_%s" % whichx)

if __name__ == "__main__":

    plotpar = {'axes.labelsize': 18,
               'text.fontsize': 26,
               'legend.fontsize': 18,
               'xtick.labelsize': 18,
               'ytick.labelsize': 18,
               'text.usetex': True}
    plt.rcParams.update(plotpar)

    whichx = str(sys.argv[1]) # should be either "rho" or "logg"

    x, y, xerr, yerr = load_data(whichx, bigdata=True)

    # load chains
    fname = "test"
    with h5py.File("%s_samples_%s.h5" % (whichx, fname), "r") as f:
        samples = f["samples"][...]
    samples = samples.T

    make_flicker_plot(x, xerr, y, yerr, samples, whichx)
    make_inverse_flicker_plot(x, xerr, y, yerr, samples, whichx, 200)
