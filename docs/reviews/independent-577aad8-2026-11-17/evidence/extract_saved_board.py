#!/usr/bin/python3
"""Read-only extraction of saved KiCad geometry; does not use repository generators."""
import json, sys
from pathlib import Path
import pcbnew as k

board = k.LoadBoard(sys.argv[1])
def pt(p): return [round(k.ToMM(p.x), 6), round(k.ToMM(p.y), 6)]
def chain(c): return [pt(c.CPoint(i)) for i in range(c.PointCount())]
data = {'kicad': k.Version(), 'source': sys.argv[1], 'footprints': [], 'tracks': [], 'zones': [], 'outline': []}
for f in board.GetFootprints():
    pads=[]
    for p in f.Pads():
        pads.append(dict(number=p.GetNumber(), net=str(p.GetNetname()), xy=pt(p.GetPosition()),
                         size=pt(p.GetSize()), drill=pt(p.GetDrillSize()), angle=p.GetOrientationDegrees(),
                         shape=int(p.GetShape()), attribute=int(p.GetAttribute()),
                         layers=[board.GetLayerName(l) for l in p.GetLayerSet().Seq()]))
    data['footprints'].append(dict(ref=f.GetReference(),value=f.GetValue(),library=str(f.GetFPID().GetLibItemName()),
                                   xy=pt(f.GetPosition()), angle=f.GetOrientationDegrees(), pads=pads))
for t in board.GetTracks():
    d=dict(net=str(t.GetNetname()),start=pt(t.GetStart()),end=pt(t.GetEnd()),width=k.ToMM(t.GetWidth(k.F_Cu) if isinstance(t,k.PCB_VIA) else t.GetWidth()),
           layer=board.GetLayerName(t.GetLayer()),uuid=str(t.m_Uuid.AsString()),type=t.GetClass())
    if isinstance(t,k.PCB_VIA):d.update(drill=k.ToMM(t.GetDrillValue()),layers=[board.GetLayerName(l) for l in t.GetLayerSet().Seq()])
    data['tracks'].append(d)
for z in board.Zones():
    for l in z.GetLayerSet().Seq():
        poly=z.GetFilledPolysList(l)
        polygons=[]
        for i in range(poly.OutlineCount()):
            polygons.append(dict(outline=chain(poly.COutline(i)), holes=[chain(poly.CHole(i,j)) for j in range(poly.HoleCount(i))]))
        data['zones'].append(dict(net=str(z.GetNetname()),layer=board.GetLayerName(l),filled=z.IsFilled(),polygons=polygons,
                                 clearance=k.ToMM(z.GetLocalClearance()),thermal_gap=k.ToMM(z.GetThermalReliefGap()),
                                 thermal_spoke=k.ToMM(z.GetThermalReliefSpokeWidth())))
for d in board.GetDrawings():
    if d.GetLayer()==k.Edge_Cuts:data['outline'].append(dict(start=pt(d.GetStart()),end=pt(d.GetEnd()),width=k.ToMM(d.GetWidth()),shape=int(d.GetShape())))
Path(sys.argv[2]).write_text(json.dumps(data,indent=2)+'\n')
print('Read saved board:',len(data['footprints']),'footprints;',len(data['tracks']),'tracks/vias;',[(z['layer'],len(z['polygons'])) for z in data['zones']])
