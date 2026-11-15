#!/usr/bin/env python3
"""Seed sensitive copper, export DSN and import a reviewed local router session.

The seed command refuses existing copper. It does not regenerate a routed PCB.
Freerouting is an optional external tool; final KiCad DRC is mandatory.
"""
import argparse
from pathlib import Path
import pcbnew as k
ROOT=Path(__file__).resolve().parents[1]
PCB=ROOT/'hardware/kicad/neuronic.kicad_pcb'
ROUTES=ROOT/'hardware/routing'
def v(xy):return k.VECTOR2I(*(k.FromMM(x) for x in xy))
def xy(point):return (k.ToMM(point.x),k.ToMM(point.y))
def main():
 ap=argparse.ArgumentParser();ap.add_argument('action',choices=['seed','import','fill']);ap.add_argument('--session',type=Path);args=ap.parse_args()
 b=k.LoadBoard(str(PCB));fps={f.GetReference():f for f in b.GetFootprints()}
 def pad(ref,num):return next(p for p in fps[ref].Pads() if p.GetNumber()==str(num))
 def trace(net,points,layer=k.F_Cu,width=.2,locked=True):
  for a,c in zip(points,points[1:]):
   if a==c:continue
   t=k.PCB_TRACK(b);t.SetStart(v(a));t.SetEnd(v(c));t.SetWidth(k.FromMM(width));t.SetLayer(layer);t.SetNetCode(b.GetNetcodeFromNetname(net));t.SetLocked(locked);b.Add(t)
 def via(net,point):
  t=k.PCB_VIA(b);t.SetPosition(v(point));t.SetWidth(k.F_Cu,k.FromMM(.6));t.SetDrill(k.FromMM(.3));t.SetViaType(k.VIATYPE_THROUGH);t.SetLayerPair(k.F_Cu,k.B_Cu);t.SetNetCode(b.GetNetcodeFromNetname(net));t.SetLocked(True);b.Add(t)
 def zone(layer):
  z=k.ZONE(b);z.SetLayer(layer);z.SetNetCode(b.GetNetcodeFromNetname('GND'));z.SetLocalClearance(k.FromMM(.25));z.SetMinThickness(k.FromMM(.2));z.SetPadConnection(k.ZONE_CONNECTION_FULL);z.SetIslandRemovalMode(k.ISLAND_REMOVAL_MODE_ALWAYS)
  poly=z.Outline();poly.NewOutline()
  for pt in [(69,55.6),(137.4,55.6),(137.4,144.4),(69,144.4)]:poly.Append(v(pt))
  b.Add(z)
 if args.action=='seed':
  if len(b.GetTracks()) or b.GetAreaCount():ap.error('Refusing to replace existing copper. Edit the routed board instead.')
  ROUTES.mkdir(exist_ok=True)
  # Seed ground zones; final review reserves In1, with In2 crossovers/fill.
  zone(k.In1_Cu);zone(k.In2_Cu)
  for i in range(1,10):
   for a,c in [((f'J{i}',1),(f'R{2*i-1}',1)),((f'R{2*i-1}',2),(f'R{2*i}',1)),((f'D{i}',3),(f'C{i}',1))]:
    p,q=pad(*a),pad(*c);assert p.GetNetCode()==q.GetNetCode()
    trace(p.GetNetname(),[xy(p.GetPosition()),xy(q.GetPosition())])
  # Direct negative-input bus inside the package, on the back layer.
  for pin in range(1,16,2):
   p=pad('U1',pin);a=xy(p.GetPosition());point=(96.4,a[1]);trace('REF_FILTERED',[a,point],width=.15);via('REF_FILTERED',point)
  trace('REF_FILTERED',[(96.4,88.25),(96.4,95.25)],k.B_Cu)
  # Supply return fanout goes inward; supply and signal pins escape outward.
  ground={20:(97.75,95.9),23:(99.25,95.9),25:(100.25,95.9),31:(103.5,95.9),32:(103.5,95.9),33:(103.5,95.9),41:(104,91.75),49:(103.75,88),51:(102.75,88),53:(101.75,88),57:(99.5,88),58:(99.5,88),62:(97.25,88)}
  placed=set()
  for pin,pt in ground.items():
   trace('GND',[xy(pad('U1',pin).GetPosition()),pt],width=.15)
   if pt not in placed:via('GND',pt);placed.add(pt)
  # Direct local connection of pin 48 to its dedicated bypass capacitor.
  trace('DVDD_3V3',[xy(pad('U1',48).GetPosition()),xy(pad('C39',1).GetPosition())])
  trace('ADS_DRDY_N',[xy(pad('U1',47).GetPosition()),(106.5,88.75),(107,89.25)],width=.15)
  via('ADS_DRDY_N',(107,89.25))
  b.BuildConnectivity();k.ZONE_FILLER(b).Fill(b.Zones());k.SaveBoard(str(PCB),b)
  k.ExportSpecctraDSN(b,str(ROUTES/'neuronic.dsn'))
  p=ROUTES/'neuronic.dsn';s=p.read_text()
  # Layer settings are router hints; check_routing.py verifies final In1 use.
  s=s.replace('(layer In1.Cu\n      (type signal)','(layer In1.Cu\n      (type power)')
  settings='    (autoroute_settings (fanout off) (autoroute on) (postroute off) (vias on)\n'
  for name,active,direction in [('F.Cu','on','horizontal'),('In1.Cu','off','horizontal'),('In2.Cu','on','horizontal'),('B.Cu','on','vertical')]:
   settings+=f'      (layer_rule {name} (active {active}) (preferred_direction {direction}))\n'
  s=s.replace('    (boundary\n',settings+'    )\n    (boundary\n')
  p.write_text(s)
  print('Saved seed copper and DSN; complete routing with the documented local router command.')
 elif args.action=='import':
  if args.session is None or not args.session.is_file():ap.error('--session must identify an existing SES file')
  if not k.ImportSpecctraSES(b,str(args.session)):raise RuntimeError('SES import failed')
  b.BuildConnectivity();k.ZONE_FILLER(b).Fill(b.Zones());k.SaveBoard(str(PCB),b)
 else:
  b.BuildConnectivity();k.ZONE_FILLER(b).Fill(b.Zones());k.SaveBoard(str(PCB),b)
if __name__=='__main__':main()
