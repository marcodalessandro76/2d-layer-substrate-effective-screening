"""Figures of the technical notes (main.tex) and of the classical models (models.tex).

Run from the Notes folder:  python make_figures.py [name ...]
Without arguments all the figures of the registry FIGURES are made. Figures are saved as jpeg in Figures/.
Lengths are in units of the sheet-substrate distance d, frequencies in units of omega_0.
"""
import os
import sys

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Figures')


def beta(eps):
    """Image coefficient (eps-1)/(eps+1) of a dielectric half-space (eps = np.inf for a metal)."""
    return 1.0 if np.isinf(eps) else (eps - 1.0) / (eps + 1.0)


def vt_over_v(Qd, eps):
    """Dressed over bare Coulomb interaction in the sheet, 1 - beta exp(-2Qd) = 1/eps_env."""
    return 1.0 - beta(eps) * np.exp(-2.0 * Qd)


def omega_L(Qd, eps, r0_over_d):
    """Longitudinal mode of the oscillator sheet, omega_L/omega_0 = sqrt(1 + r0 Q / eps_env(Q))."""
    return np.sqrt(1.0 + r0_over_d * Qd * vt_over_v(Qd, eps))


def fig_vt_ratio():
    """Dressed over bare interaction in a plane above a dielectric half-space (main notes, Sec. 2.3)."""
    Qd = np.linspace(1e-4, 2.0, 801)
    fig, ax = plt.subplots(figsize=(4.6, 3.4))
    for eps in [2.0, 4.0, 10.0, np.inf]:
        lab = r'metal' if np.isinf(eps) else r'$\varepsilon = %g$' % eps
        ax.plot(Qd, vt_over_v(Qd, eps), label=lab)
    ax.set_xlim(0.0, 2.0)
    ax.set_ylim(0.0, 1.02)
    ax.set_xlabel(r'$Qd$')
    ax.set_ylabel(r'$\tilde{v}(Q)/v(Q) = 1/\varepsilon_{\mathrm{env}}(Q)$')
    ax.legend(frameon=False, fontsize=9)
    fig.tight_layout()
    return fig


def fig_sheet_modes():
    """Interaction ratio and longitudinal mode of the oscillator sheet (models notes)."""
    Qd = np.linspace(1e-4, 2.0, 801)
    fig, axs = plt.subplots(1, 2, figsize=(9.0, 3.6))
    ax = axs[0]
    for eps in [2.0, 4.0, 10.0, np.inf]:
        lab = r'metal' if np.isinf(eps) else r'$\varepsilon = %g$' % eps
        ax.plot(Qd, vt_over_v(Qd, eps), label=lab)
    ax.set_xlim(0.0, 2.0)
    ax.set_ylim(0.0, 1.02)
    ax.set_xlabel(r'$Qd$')
    ax.set_ylabel(r'$\tilde{v}(Q)/v(Q) = 1/\varepsilon_{\mathrm{env}}(Q)$')
    ax.legend(frameon=False, fontsize=9)
    ax.set_title('(a)', loc='left', fontsize=10)
    ax = axs[1]
    r0 = 5.0
    for eps, lab in [(1.0, 'free-standing'), (4.0, r'$\varepsilon = 4$'), (np.inf, 'metal')]:
        ax.plot(Qd, omega_L(Qd, eps, r0), label=lab)
    ax.axhline(1.0, color='k', lw=0.6, ls=':')
    ax.text(1.98, 1.03, r'$\omega_T = \omega_0$', ha='right', va='bottom', fontsize=9)
    ax.set_xlim(0.0, 2.0)
    ax.set_xlabel(r'$Qd$')
    ax.set_ylabel(r'$\omega_L(Q)/\omega_0$')
    ax.legend(frameon=False, fontsize=9, loc='upper left')
    ax.set_title(r'(b) $r_0 = 5d$', loc='left', fontsize=10)
    fig.tight_layout()
    return fig


FIGURES = {
    'vt_ratio': fig_vt_ratio,          # main.tex
    'sheet_modes': fig_sheet_modes,    # models.tex
}


if __name__ == '__main__':
    names = sys.argv[1:] or list(FIGURES)
    os.makedirs(OUT_DIR, exist_ok=True)
    for name in names:
        fig = FIGURES[name]()
        path = os.path.join(OUT_DIR, name + '.jpeg')
        fig.savefig(path, dpi=200, pil_kwargs={'quality': 92})
        plt.close(fig)
        print('saved', path)
