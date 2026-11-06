"""Figures of the technical notes.

Run from the Notes folder:  python make_figures.py [name ...]
Without arguments all the figures of the registry FIGURES are made. Figures are saved as jpeg in Figures/.
Lengths are in units of the sheet-substrate distance d (of the wavelength for charge_wave_field), frequencies in
units of omega_0, potentials in units of sigma_Q / (2 eps0 Q).
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


def potential_profile(z, Qd, eps):
    """Potential of a charge wave in the plane z = 1 (units of d) above a substrate in z < 0.

    Returns phi_Q(z) in units of 2 pi sigma_Q / Q.
    """
    b = beta(eps)
    out = np.exp(-Qd * np.abs(z - 1.0)) - b * np.exp(-Qd * (z + 1.0))
    inside = (1.0 - b) * np.exp(Qd * (z - 1.0))
    return np.where(z >= 0.0, out, inside)


def vt_over_v(Qd, eps):
    """Dressed over bare Coulomb interaction in the sheet, 1 - beta exp(-2Qd) = 1/eps_env."""
    return 1.0 - beta(eps) * np.exp(-2.0 * Qd)


def omega_L(Qd, eps, r0_over_d):
    """Longitudinal mode of the oscillator sheet, omega_L/omega_0 = sqrt(1 + r0 Q / eps_env(Q))."""
    return np.sqrt(1.0 + r0_over_d * Qd * vt_over_v(Qd, eps))


def fig_charge_wave_field():
    """Field lines and potential of a charged plane z = 0: (a) uniform density, (b) charge wave cos(Qx).

    Lengths in units of the wavelength lambda = 2 pi / Q. The field lines of (b) start just above/below the
    positive stripes and are integrated along E, so they end on the negative stripes.
    """
    Q = 2.0 * np.pi
    xmax, zmax = 2.0, 0.6
    x = np.linspace(0.0, xmax, 400)
    z = np.linspace(-zmax, zmax, 400)          # even number of points: z = 0 is not on the grid
    X, Z = np.meshgrid(x, z)
    norm = matplotlib.colors.Normalize(vmin=-1.0, vmax=1.0)
    cmap = 'RdBu_r'
    fig, axs = plt.subplots(1, 2, figsize=(9.0, 3.4))

    # (a) uniform plane: E = sgn(z) z-hat, phi linear in |z| (constant chosen to fill the colour scale)
    ax = axs[0]
    ax.contourf(X, Z, 1.0 - 2.0 * np.abs(Z) / zmax, levels=41, cmap=cmap, norm=norm)
    starts = [(xs, s * 0.02) for xs in np.linspace(0.1, xmax - 0.1, 10) for s in (1.0, -1.0)]
    ax.streamplot(X, Z, np.zeros_like(X), np.sign(Z), start_points=starts, integration_direction='forward',
                  color='k', linewidth=0.8, arrowsize=0.8, broken_streamlines=False)
    ax.plot([0.0, xmax], [0.0, 0.0], color='C3', lw=3.0, solid_capstyle='butt', zorder=3)
    for xs in np.linspace(0.3, xmax - 0.3, 4):
        ax.text(xs, 0.0, '+', ha='center', va='center', fontsize=9, fontweight='bold', zorder=4,
                bbox=dict(boxstyle='circle,pad=0.15', facecolor='white', edgecolor='C3'))
    ax.set_title(r'(a) $\mathbf{Q} = 0$: uniform plane', loc='left', fontsize=10)
    ax.set_xlabel(r'$x$')
    ax.set_ylabel(r'$z$')
    ax.set_xticks([])
    ax.set_yticks([])

    # (b) charge wave: phi = cos(Qx) exp(-Q|z|), E = -grad phi
    ax = axs[1]
    decay = np.exp(-Q * np.abs(Z))
    ax.contourf(X, Z, np.cos(Q * X) * decay, levels=41, cmap=cmap, norm=norm)
    Ex = Q * np.sin(Q * X) * decay
    Ez = Q * np.cos(Q * X) * np.sign(Z) * decay
    offsets = [0.004, 0.012, 0.03, 0.06, 0.1, 0.16]
    centres = [0.0, 1.0, 2.0]
    xs_list = [c + s * o for c in centres for o in offsets for s in (1.0, -1.0) if 0.0 < c + s * o < xmax]
    starts = [(xs, s * 0.01) for xs in xs_list for s in (1.0, -1.0)]
    ax.streamplot(X, Z, Ex, Ez, start_points=starts, integration_direction='forward', color='k', linewidth=0.8,
                  arrowsize=0.8, broken_streamlines=False)
    xl = np.linspace(0.0, xmax, 801)
    stripe = np.where(np.cos(Q * xl) >= 0.0, 1.0, np.nan)
    ax.plot(xl, 0.0 * stripe, color='C3', lw=3.0, zorder=3)
    ax.plot(xl, 0.0 * (np.where(np.isnan(stripe), 1.0, np.nan)), color='C0', lw=3.0, zorder=3)
    for xc, sign, c in [(1.0, '+', 'C3'), (0.5, r'$-$', 'C0'), (1.5, r'$-$', 'C0')]:
        ax.text(xc, 0.0, sign, ha='center', va='center', fontsize=9, fontweight='bold', zorder=4,
                bbox=dict(boxstyle='circle,pad=0.15', facecolor='white', edgecolor=c))
    for zl in (1.0 / Q, -1.0 / Q):
        ax.axhline(zl, color='k', lw=0.6, ls=':')
    ax.text(1.0, 1.0 / Q + 0.015, r'$|z| = 1/Q$', ha='center', va='bottom', fontsize=8,
            bbox=dict(boxstyle='square,pad=0.1', facecolor='white', edgecolor='none'))
    ax.set_title(r'(b) $\mathbf{Q} \neq 0$: charge wave $\propto\cos(Qx)$', loc='left', fontsize=10)
    ax.set_xlabel(r'$x/\lambda$')
    ax.set_ylabel(r'$z/\lambda$')
    for ax in axs:
        ax.set_xlim(0.0, xmax)
        ax.set_ylim(-zmax, zmax)
        ax.set_aspect('equal')
    fig.tight_layout()
    return fig


def fig_sheet_potential():
    z = np.linspace(-2.0, 5.0, 1401)
    fig, ax = plt.subplots(figsize=(6.0, 3.6))
    ax.axvspan(-2.0, 0.0, color='0.88', lw=0)
    ax.text(-1.0, 1.02, r'substrate ($\varepsilon=4$)', ha='center', va='top', fontsize=9)
    colors = ['C0', 'C1', 'C2']
    for Qd, c in zip([0.25, 1.0, 3.0], colors):
        ax.plot(z, potential_profile(z, Qd, 4.0), color=c, label=r'$Qd = %g$' % Qd)
        ax.plot(z, potential_profile(z, Qd, 1.0), color=c, ls='--', lw=1.0)
    ax.axvline(1.0, color='k', lw=0.6, ls=':')
    ax.text(1.05, 0.05, 'sheet', fontsize=9)
    ax.set_xlim(-2.0, 5.0)
    ax.set_ylim(0.0, 1.05)
    ax.set_xlabel(r'$z/d$')
    ax.set_ylabel(r'$\phi_{\mathbf{Q}}(z)\,/\,[\sigma_{\mathbf{Q}}/(2\varepsilon_0 Q)]$')
    ax.legend(frameon=False, fontsize=9)
    fig.tight_layout()
    return fig


def fig_sheet_modes():
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
    'charge_wave_field': fig_charge_wave_field,
    'sheet_potential': fig_sheet_potential,
    'sheet_modes': fig_sheet_modes,
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
