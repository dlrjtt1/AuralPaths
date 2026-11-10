"""
Prototype check of the seat-dip model (seatdip.py, 2-D BEM) on BRAS RS7 (15 blocks 0.24 m high on a hard floor;
Aspoeck et al., https://doi.org/10.14279/depositonce-6726.3, CC BY-SA 4.0): the 3-D direct sound times the 2-D
transfer function T(f), windowed and compared in third-octave bands with the measured RIRs as in validation/bras_rs.py.
Also checks the BEM against the analytic solution for a rigid half-cylinder on a rigid floor.

    python validation/rs7_seatdip_bem.py <folder holding "_unz/1 Scene descriptions">
"""
import sys,os,math,time
import numpy as np
from scipy.special import hankel1, jvp, h1vp
HERE=os.path.dirname(os.path.abspath(__file__))
sys.path[:0]=[os.path.join(HERE,'..'),HERE]
import bras_rs as b, seatdip as sd

def check_cylinder():
    """BEM vs the series solution for a rigid half-cylinder (radius 0.3 m) on a rigid floor, line source."""
    a, S0 = 0.3, np.array([-2.0, 0.5])
    Rs = np.array([[1.5, 0.3], [0.0, 0.6], [3.0, 0.05], [-0.5, 1.0]])
    th = np.linspace(0, np.pi, 400)
    semi = np.c_[a * np.cos(th), a * np.sin(th)]
    worst = 0.0
    for fr in (200, 800, 2000):
        k = 2 * np.pi * fr / 343
        T = sd.transfer([semi], S0, Rs, np.array([fr]), c=343)[0]
        ref = []
        for x in Rs:
            p = 0
            for src in (S0, S0 * np.array([1, -1])):
                rs, ps = np.hypot(*src), np.arctan2(src[1], src[0])
                r, ph = np.hypot(*x), np.arctan2(x[1], x[0])
                p += 0.25j * hankel1(0, k * np.hypot(*(x - src)))
                for n in range(80):
                    p -= 0.25j * (1 if n == 0 else 2) * jvp(n, k * a) / h1vp(n, k * a) * hankel1(n, k * rs) * \
                        hankel1(n, k * r) * np.cos(n * (ph - ps))
            ref.append(p / (0.25j * hankel1(0, k * np.hypot(*(x - S0)))))
        worst = max(worst, float(np.max(np.abs(20 * np.log10(np.abs(T) / np.abs(ref))))))
    print(f"BEM vs analytic half-cylinder: max level difference {worst:.3f} dB")


check_cylinder()

root=sys.argv[1]
sdir=b.find_scene_dir(root,"RS7")
ir,E,R,eid,rid=b.read_sofa(os.path.join(sdir,"RIRs","RS7_RIRs.sofa"))
nfft=1<<int(math.ceil(math.log2(ir.shape[1]))); FS=b.FS
f=np.fft.rfftfreq(nfft,1/FS); c=331.3*math.sqrt(1+b.TEMP["RS7"]/273.15); air=b.air_np(f,b.TEMP["RS7"],b.HUM["RS7"])
blocks=[[(x-0.06,0),(x+0.06,0),(x+0.06,0.24),(x-0.06,0.24)] for x in [3.958+0.34*r for r in range(15)]]
fg=np.geomspace(40,6000,180)
TH=np.array(b.THIRD); sel=(TH>=125)&(TH<=4000)
for i in range(len(eid)):
    S,Rr=E[i],R[i]; t=time.time()
    T=sd.transfer(blocks,[S[0],S[2]],[Rr[0],Rr[2]],fg,c=c)
    mag=np.interp(np.log(np.maximum(f,40)),np.log(fg),np.abs(T)); ph=np.interp(np.log(np.maximum(f,40)),np.log(fg),np.unwrap(np.angle(T)))
    L=float(np.linalg.norm(Rr-S)); H=b.P1M*np.exp(-1j*2*np.pi*f/c*L-air*L)/L*mag*np.exp(1j*ph)
    taper=np.clip((12000-f)/2000,0,1)
    xs=np.fft.irfft(H*taper,nfft); xm=np.zeros(nfft); xm[:ir.shape[1]]=ir[i]; t0=L/c
    lm=b.third_levels(b.window(xm,b.WIN["RS7"],t0),nfft); ls=b.third_levels(b.window(xs,b.WIN["RS7"],t0),nfft)
    d=(lm-ls)[sel]
    print(f"LS{eid[i]}-MP{rid[i]} bias {np.median(d):+.1f} shape {np.sqrt(np.mean((d-d.mean())**2)):.1f} mad {np.mean(np.abs(d)):.1f}  ({time.time()-t:.0f}s)", " ".join(f"{x:+.0f}" for x in d), flush=True)
