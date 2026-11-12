# Miw's Town: the desserts on Cheesecake Rush's menu, sculpted in Blender.
#   /Applications/Blender.app/Contents/MacOS/Blender -b -P shared/models/menu.py -- shared/models/kittycupcake.glb [preview.png]
# The output file's name picks the dessert. Each sits on the table at its origin, about 0.6 across, facing +z.
#   cheesecake — a slice of strawberry cheesecake, the shop's own
#   pretzelcake  — a slice of vanilla-caramel layer cake with a pink zigzag and a mini pretzel on top
#   kittycupcake — a cupcake whose frosting is a tabby cat's face, in a polka-dot wrapper like Miw's dress
#   donut        — a strawberry-glazed donut with a cream zigzag and golden sprinkles
#   pancake      — a stack of three strawberry pancakes with maple syrup, a pat of butter and cream
#   macaron      — three pastel macarons (pink, mint, lilac) with a strawberry
#   honeytoast   — a thick block of honey toast, cut in a crosshatch, with butter, honey running down, a scoop of cream and a strawberry
#   pudding      — a wobbly custard pudding turned out of its cup: caramel on top running down the sides, a pool of caramel, cream and a strawberry
#   bingsu       — Korean milk-snow bingsu: a mound of shaved milk snow in a bowl, condensed milk running down it, strawberries round it and a scoop of strawberry ice cream on top
#   festivalcake — the town festival's three-tier cake: pink, vanilla and lilac tiers with cream drips, strawberries, sparklers and a gold star
#   matcharoll   — a slice of matcha Swiss roll standing on its edge: a green sponge round a cream spiral, cream, a strawberry and a dusting of matcha
#   cheesefull, pretzelfull — the whole round cakes that go in the oven; a batch is cut into four slices
# Written in Blender's own coordinates (z up, the front faces -y), like the characters.
import os, sys, random; sys.path.insert(0, os.path.dirname(__file__))
from kit import *
from kit import _mesh_object

WHO = os.path.splitext(os.path.basename(OUT))[0]
BUILT = {}
def dessert(fn):
    BUILT[fn.__name__] = fn
    return fn

def wedge(name, parent, r, a, z0, h, mat, bevel=0.02, grow=0.0):
    """A slice of a round cake: a sector of angle a and radius r, from height z0 up by h, its point at the origin
    and its curved back towards +y (so the cut faces show from the front). grow pushes every face out a little."""
    bm = bmesh.new()
    n = 12
    tip = (0, -grow * 1.4)
    pts = [tip] + [((r + grow) * math.sin(-a / 2 + a * i / n), (r + grow) * math.cos(-a / 2 + a * i / n)) for i in range(n + 1)]
    bot = [bm.verts.new((x, y, z0 - grow)) for x, y in pts]
    top = [bm.verts.new((x, y, z0 + h + grow)) for x, y in pts]
    bm.faces.new(list(reversed(bot))); bm.faces.new(top)
    for i in range(len(pts)):
        j = (i + 1) % len(pts)
        bm.faces.new((bot[i], bot[j], top[j], top[i]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    if bevel: bmesh.ops.bevel(bm, geom=list(bm.edges), offset=bevel, segments=3, profile=0.5, affect='EDGES')
    o = _mesh_object(name, parent, (0, 0, 0), bm, mat)
    big = max(p.area for p in o.data.polygons)
    for p in o.data.polygons: p.use_smooth = p.area < big * 0.04
    return o

def wedge_edge(r, a, steps):
    """Points round the top edge of a wedge, with the outward direction at each: down one cut face, across the
    curved back, and up the other cut face."""
    out = []
    # the cut face at angle t runs from the tip along (sin t, cos t); its outward normal is (side*cos t, -side*sin t)
    for side in (-1, 1):
        t = side * a / 2
        d, nrm = Vector((math.sin(t), math.cos(t), 0)), Vector((side * math.cos(t), -side * math.sin(t), 0))
        for k in range(steps):
            out.append((d * r * (0.18 + 0.78 * k / max(1, steps - 1)), nrm))
    for k in range(steps * 2):
        t = -a / 2 + a * (k + 0.5) / (steps * 2)
        d = Vector((math.sin(t), math.cos(t), 0))
        out.append((d * r, d))
    return out

def drips(name, parent, r, a, z, mat, thick, steps, seed, long=0.12):
    """Glaze running down the sides of a wedge from height z."""
    rnd = random.Random(seed)
    for i, (p, nrm) in enumerate(wedge_edge(r, a, steps)):
        ln = long * (0.35 + rnd.random())
        at = p + nrm * thick * 0.55
        blob(f'{name}_{i}', parent, (at.x, at.y, z - ln * 0.5), (thick, thick, ln * 0.5 + thick), mat, seg=12, ring=8)
        blob(f'{name}_tip_{i}', parent, (at.x, at.y, z - ln), (thick * 1.15,) * 3, mat, seg=12, ring=8)

def strawberry(parent, name, loc, s=1.0):
    x, y, z = loc
    blob(f'{name}_body', parent, (x, y, z + 0.06 * s), (0.07 * s, 0.07 * s, 0.085 * s), C('#f04466', 0.3), seg=18, ring=10,
         shape=lambda co: co.__setitem__(2, co.z if co.z > 0 else co.z * (1 + 0.35 * -co.z)))
    blob(f'{name}_shine', parent, (x - 0.028 * s, y - 0.052 * s, z + 0.1 * s), (0.013 * s, 0.007 * s, 0.022 * s), C('#fff3f5', 0.25), rot=(0, 0.45, 0), seg=10, ring=6)   # the glossy highlight
    for k in range(5):
        t = k / 5 * 2 * math.pi
        blob(f'{name}_leaf_{k}', parent, (x + math.cos(t) * 0.03 * s, y + math.sin(t) * 0.03 * s, z + 0.14 * s),
             (0.04 * s, 0.016 * s, 0.01 * s), C('#7cc68a'), rot=(0, 0, t), seg=8, ring=6)
    for k in range(7):
        t = k / 7 * 2 * math.pi + 0.3
        blob(f'{name}_seed_{k}', parent, (x + math.cos(t) * 0.066 * s, y + math.sin(t) * 0.066 * s, z + (0.04 + 0.04 * (k % 2)) * s),
             (0.007 * s,) * 3, C('#fff1a8'), seg=6, ring=4)

def blueberry(parent, name, loc, s=1.0):
    x, y, z = loc
    blob(f'{name}_body', parent, (x, y, z + 0.035 * s), (0.04 * s, 0.04 * s, 0.037 * s), C('#6c7fe0', 0.3), seg=14, ring=9)
    blob(f'{name}_crown', parent, (x, y, z + 0.068 * s), (0.012 * s, 0.012 * s, 0.006 * s), C('#3f4aa8', 0.5), seg=8, ring=5)
    blob(f'{name}_shine', parent, (x - 0.014 * s, y - 0.026 * s, z + 0.05 * s), (0.008 * s, 0.005 * s, 0.011 * s), C('#f4f6ff', 0.25), rot=(0, 0.4, 0), seg=8, ring=5)

def mint(parent, name, loc, s=1.0, rot=0.0):
    x, y, z = loc
    blob(f'{name}_a', parent, (x, y, z), (0.05 * s, 0.026 * s, 0.011 * s), C('#6fcf93', 0.45), rot=(0, 0, rot), seg=10, ring=6)
    blob(f'{name}_b', parent, (x + math.cos(rot + 2.2) * 0.04 * s, y + math.sin(rot + 2.2) * 0.04 * s, z - 0.004 * s), (0.04 * s, 0.022 * s, 0.01 * s), C('#8fdca7', 0.45), rot=(0, 0, rot + 2.2), seg=10, ring=6)

# ---------- 🍰 strawberry cheesecake ----------
@dessert
def cheesecake(g):
    s = node('slice', g, (0, -0.12, 0))
    r, a = 0.42, 0.95
    wedge('crust', s, r, a, 0, 0.07, C('#c98b4b', 0.8))
    wedge('cake', s, r, a, 0.07, 0.2, C('#fff0cf', 0.55))
    wedge('glaze', s, r, a, 0.27, 0.035, C('#f48fa8', 0.3), grow=0.008)
    drips('drip', s, r + 0.008, a, 0.28, C('#f48fa8', 0.3), 0.018, 3, 4, long=0.09)
    for k, t in enumerate((-0.2, 0.2)):   # piped cream along the back, with a strawberry sitting in it
        blob(f'puff_{k}', s, (math.sin(t) * r * 0.8, math.cos(t) * r * 0.8, 0.33), (0.045, 0.045, 0.035), C('#fffaf3', 0.5), seg=14, ring=8)
    strawberry(s, 'berry', (0, r * 0.72, 0.3), 1.0)

# ---------- 🥨 caramel pretzel cake ----------
# the same rope the pages' makePretzel() follows (scenery.js), in its XY plane
PRETZEL_PATH = [(-0.55, -0.15, 0.02), (-0.3, 0.05, 0.05), (-0.06, 0.3, 0.08), (0.2, 0.56, 0.02), (0.5, 0.68, 0), (0.74, 0.5, 0), (0.8, 0.15, 0),
                (0.66, -0.26, 0), (0.36, -0.52, 0), (0, -0.6, 0), (-0.36, -0.52, 0), (-0.66, -0.26, 0), (-0.8, 0.15, 0), (-0.74, 0.5, 0),
                (-0.5, 0.68, 0), (-0.2, 0.56, 0.02), (0.06, 0.3, -0.08), (0.3, 0.05, -0.05), (0.55, -0.15, 0.02)]

def pretzel(name, parent, loc, s, tilt=0.0):
    """A little salted pretzel standing up, facing the front."""
    p = node(name, parent, loc)
    p.rotation_euler = (tilt, 0, 0)
    pts = [(x * s, -z * s, y * s) for x, y, z in PRETZEL_PATH]
    tube(f'{name}_dough', p, pts, [1] * len(pts), C('#c98a4b', 0.6), bevel=0.13 * s)
    rnd = random.Random(7)
    for k in range(9):
        x, y, z = PRETZEL_PATH[rnd.randrange(1, len(PRETZEL_PATH) - 1)]
        blob(f'{name}_salt_{k}', p, ((x + (rnd.random() - 0.5) * 0.1) * s, -0.12 * s, (y + (rnd.random() - 0.5) * 0.1) * s), (0.035 * s,) * 3, C('#ffffff', 0.4), seg=6, ring=4)

@dessert
def pretzelcake(g):
    s = node('slice', g, (0, -0.14, 0))
    r, a = 0.46, 0.9
    wedge('biscuit', s, r, a, 0, 0.07, C('#e8b886', 0.8))
    wedge('sponge_lo', s, r, a, 0.07, 0.11, C('#fff0cf', 0.7))
    wedge('caramel', s, r, a, 0.18, 0.035, C('#e59a4c', 0.35), bevel=0.012)
    wedge('sponge_hi', s, r, a, 0.215, 0.11, C('#fff0cf', 0.7))
    wedge('icing', s, r, a, 0.325, 0.035, C('#eda95e', 0.3), grow=0.01)   # caramel, the color of the pretzel
    drips('drip', s, r + 0.01, a, 0.335, C('#eda95e', 0.3), 0.02, 3, 9, long=0.12)
    # a swirl of cream holding up a mini pretzel, with a zigzag of the town's pink icing across the top
    blob('cream', s, (0, r * 0.66, 0.39), (0.075, 0.06, 0.045), C('#fffaf3', 0.5), seg=18, ring=10)
    pretzel('pretzel', s, (0, r * 0.66, 0.49), 0.1, tilt=-0.15)
    zig = [((-1) ** k * 0.03 * (1 + k * 0.25), r * (0.22 + 0.045 * k), 0.37) for k in range(7)]
    tube('drizzle', s, zig, [1] * len(zig), C('#f9cdd9', 0.4), bevel=0.012)
    for k, t in enumerate((-0.28, 0.28)):   # little piped rosettes beside the pretzel, each with a pink dot
        blob(f'rosette_{k}', s, (math.sin(t) * r * 0.8, math.cos(t) * r * 0.8, 0.355), (0.04, 0.04, 0.03), C('#fffaf3', 0.5), seg=14, ring=8)
        blob(f'rosette_dot_{k}', s, (math.sin(t) * r * 0.8, math.cos(t) * r * 0.8, 0.385), (0.014, 0.014, 0.012), C('#f4a1b8', 0.3), seg=8, ring=6)

# ---------- 🐱 kitty cupcake ----------
@dessert
def kittycupcake(g):
    # a polka-dot paper wrapper, like Miw's dress
    wrap = lathe('wrapper', g, (0, 0, 0), [(0.0005, 0.3), (0.24, 0.3), (0.255, 0.28), (0.19, 0.015), (0.17, 0.0), (0.0005, 0.0)], C('#ffc4d6', 0.75), seg=96)
    for v in wrap.data.vertices:
        if math.hypot(v.co.x, v.co.y) > 0.01:
            k = 1 + 0.04 * abs(math.cos(math.atan2(v.co.y, v.co.x) * 9))
            v.co.x *= k; v.co.y *= k
    for p in wrap.data.polygons: p.use_smooth = True
    for row, z in enumerate((0.08, 0.19)):
        rr = 0.17 + (0.24 - 0.17) * z / 0.3 + 0.012
        for k in range(9):
            t = (k + row * 0.5) / 9 * 2 * math.pi
            blob(f'dot_{row}_{k}', g, (math.cos(t) * rr, math.sin(t) * rr, z), (0.018, 0.018, 0.018), C('#ffffff', 0.5), seg=8, ring=6)
    # the frosting is a round tabby face
    fx, fy, fz = 0.25, 0.25, 0.2
    face = C('#ffd1a6', 0.5)
    blob('frosting', g, (0, 0, 0.32), (fx, fy, fz), face, seg=32, ring=16)
    def on_face(x, z, out=0.0):
        y = -fy * math.sqrt(max(0.0, 1 - (x / fx) ** 2 - ((z - 0.32) / fz) ** 2))
        return (x, y - out, z)
    def point(co):   # round at the bottom, pointed at the top
        k = max(0.0, co.z)
        co.x *= 1 - 0.8 * k; co.y *= 1 - 0.8 * k
    for sd in (-1, 1):
        blob(f'ear_{sd}', g, (sd * 0.14, 0, 0.47), (0.08, 0.05, 0.1), face, rot=(0, sd * 0.35, 0), seg=16, ring=10, shape=point)
        blob(f'ear_in_{sd}', g, (sd * 0.137, -0.03, 0.465), (0.05, 0.02, 0.07), C('#ffb3c6', 0.6), rot=(0, sd * 0.35, 0), seg=12, ring=8, shape=point)
        blob(f'eye_{sd}', g, on_face(sd * 0.08, 0.4, -0.005), (0.026, 0.02, 0.03), C('#4b3442', 0.25), seg=12, ring=8)
        blob(f'blush_{sd}', g, on_face(sd * 0.15, 0.35, -0.003), (0.035, 0.012, 0.022), C('#ff9bb0', 0.8), seg=10, ring=6)
        for k, z in enumerate((0.47, 0.44)):   # tabby stripes on the forehead
            blob(f'stripe_{sd}_{k}', g, on_face(sd * 0.035, z, -0.002), (0.012, 0.01, 0.03), C('#e8a06a', 0.5), rot=(0, sd * 0.4, 0), seg=8, ring=6)
    x0, y0, z0 = on_face(0, 0.36, 0.004)
    tube('mouth', g, [(x0 - 0.035, y0, z0 + 0.008), (x0 - 0.018, y0 - 0.002, z0 - 0.008), (x0, y0, z0), (x0 + 0.018, y0 - 0.002, z0 - 0.008), (x0 + 0.035, y0, z0 + 0.008)],
         [1] * 5, C('#4b3442'), bevel=0.006)
    # a strawberry tucked between the ears
    strawberry(g, 'berry', (0.0, 0.05, 0.5), 0.75)

# ---------- 🍩 strawberry donut ----------
@dessert
def donut(g):
    R_, r = 0.22, 0.11
    def torus_mesh(name, rad, mat, seg=64, sides=24):
        bm = bmesh.new()
        vs = [[None] * sides for _ in range(seg)]
        for i in range(seg):
            th = 2 * math.pi * i / seg
            for j in range(sides):
                ph = 2 * math.pi * j / sides
                rr = rad(th, ph)
                vs[i][j] = bm.verts.new(((R_ + rr * math.cos(ph)) * math.cos(th), (R_ + rr * math.cos(ph)) * math.sin(th), r + rr * math.sin(ph) * 0.92))
        for i in range(seg):
            for j in range(sides):
                bm.faces.new((vs[i][j], vs[(i + 1) % seg][j], vs[(i + 1) % seg][(j + 1) % sides], vs[i][(j + 1) % sides]))
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        return _mesh_object(name, g, (0, 0, 0), bm, mat)
    def surface(th, ph, rr):
        return ((R_ + rr * math.cos(ph)) * math.cos(th), (R_ + rr * math.cos(ph)) * math.sin(th), r + rr * math.sin(ph) * 0.92)
    torus_mesh('dough', lambda th, ph: r, C('#eeb36c', 0.8))
    # strawberry glaze over the top half, running down in wavy drips; below its edge it tucks inside the dough
    def glaze(th, ph):
        edge = -0.4 + 0.22 * math.sin(th * 7) + 0.12 * math.sin(th * 13 + 1)
        k = max(0.0, min(1.0, (math.sin(ph) - edge) / 0.18 + 0.5))
        return r * (0.9 + 0.17 * k)
    torus_mesh('glaze', glaze, C('#f78db1', 0.3), seg=96, sides=32)
    # a zigzag of cream drizzled all the way round, from the outer edge to the inner one and back
    corner = lambda k: (2 * math.pi * k / 22, 0.6 if k % 2 else 2.5)
    zig = [surface(*[c0 + (c1 - c0) * u / 6 for c0, c1 in zip(corner(k), corner(k + 1))], r * 1.1) for k in range(22) for u in range(6)]
    tube('drizzle', g, zig, [1] * len(zig), C('#fffaf3', 0.5), bevel=0.011)
    # little pretzel-gold and white sprinkles
    rnd = random.Random(5)
    cols = ['#ffd84a', '#fffaf3', '#7fd6a8', '#b39af2', '#ff5d8f']
    for k in range(46):
        th, ph = rnd.random() * 2 * math.pi, 0.45 + rnd.random() * 2.2
        x, y, z = surface(th, ph, r * 1.07)
        blob(f'sprinkle_{k}', g, (x, y, z), (0.026, 0.009, 0.009), C(cols[k % 5], 0.4), rot=(0, rnd.random() * 3, rnd.random() * 3), seg=8, ring=6)

# ---------- whole cakes: what goes in the oven (a batch is cut into four slices) ----------
def disk(name, parent, r, z0, h, mat, rd=0.02):
    """A round layer from height z0 up by h, its rims softly rounded."""
    return lathe(name, parent, (0, 0, 0), [(0.0005, z0 + h), (r - rd, z0 + h), (r, z0 + h - rd), (r, z0 + rd), (r - rd, z0), (0.0005, z0)], mat, seg=64)

def ring_drips(name, parent, r, z, mat, th, n, seed, long=0.1):
    """Glaze running down the side of a round cake from height z."""
    rnd = random.Random(seed)
    for k in range(n):
        a = k / n * 2 * math.pi + rnd.random() * 0.1
        ln = long * (0.35 + rnd.random())
        x, y = r * math.cos(a), r * math.sin(a)
        blob(f'{name}_{k}', parent, (x, y, z - ln * 0.5), (th, th, ln * 0.5 + th), mat, seg=12, ring=8)
        blob(f'{name}_tip_{k}', parent, (x, y, z - ln), (th * 1.15,) * 3, mat, seg=12, ring=8)

@dessert
def cheesefull(g):
    s = node('cake', g)
    r = 0.42
    disk('crust', s, r, 0, 0.07, C('#c98b4b', 0.8))
    disk('cake', s, r - 0.005, 0.07, 0.2, C('#fff0cf', 0.55))
    disk('glaze', s, r + 0.008, 0.27, 0.035, C('#f48fa8', 0.3), rd=0.012)
    ring_drips('drip', s, r + 0.01, 0.28, C('#f48fa8', 0.3), 0.02, 16, 3)
    for k in range(6):   # strawberries round the top, a cream puff between each
        a = k / 6 * 2 * math.pi
        strawberry(s, f'berry_{k}', (0.28 * math.cos(a), 0.28 * math.sin(a), 0.3), 0.8)
        b = a + math.pi / 6
        blob(f'puff_{k}', s, (0.28 * math.cos(b), 0.28 * math.sin(b), 0.31), (0.05, 0.05, 0.04), C('#fffaf3', 0.5), seg=14, ring=8)
    strawberry(s, 'berry_mid', (0, 0, 0.3), 1.1)

@dessert
def pretzelfull(g):
    s = node('cake', g)
    r = 0.44
    disk('biscuit', s, r, 0, 0.07, C('#e8b886', 0.8))
    disk('sponge_lo', s, r - 0.004, 0.07, 0.11, C('#fff0cf', 0.7))
    disk('caramel', s, r, 0.18, 0.035, C('#e59a4c', 0.35), rd=0.012)
    disk('sponge_hi', s, r - 0.004, 0.215, 0.11, C('#fff0cf', 0.7))
    disk('icing', s, r + 0.008, 0.325, 0.035, C('#eda95e', 0.3), rd=0.012)
    ring_drips('drip', s, r + 0.01, 0.335, C('#eda95e', 0.3), 0.02, 18, 9, long=0.12)
    blob('cream', s, (0, 0, 0.38), (0.13, 0.13, 0.05), C('#fffaf3', 0.5), seg=18, ring=10)
    pretzel('pretzel', s, (0, 0, 0.5), 0.17, tilt=-0.15)
    for k in range(8):   # a ring of little pink icing dots
        a = k / 8 * 2 * math.pi
        blob(f'dot_{k}', s, (0.3 * math.cos(a), 0.3 * math.sin(a), 0.36), (0.035, 0.035, 0.03), C('#f9cdd9', 0.4), seg=10, ring=6)

# ---------- 🥞 strawberry pancakes ----------
@dessert
def pancake(g):
    # three fluffy pancakes, the top one a little paler, with golden edges
    for i, (r, z0, col) in enumerate([(0.30, 0.0, '#e8aa48'), (0.285, 0.085, '#efb85a'), (0.292, 0.17, '#f6c870')]):
        disk(f'cake_{i}', g, r, z0, 0.092, C(col, 0.75), rd=0.04)
        disk(f'band_{i}', g, r + 0.004, z0 + 0.034, 0.026, C('#fff2cf', 0.8), rd=0.012)   # the pale fluffy middle of each pancake
    # maple syrup pooled on top and running down the sides
    blob('syrup', g, (0, 0, 0.262), (0.235, 0.235, 0.03), C('#d9792b', 0.2), seg=32, ring=10)
    ring_drips('syrup_drip', g, 0.285, 0.272, C('#d9792b', 0.25), 0.026, 7, 4, long=0.1)
    blob('butter', g, (-0.06, 0.04, 0.3), (0.075, 0.07, 0.03), C('#ffe27a', 0.4), rot=(0, 0, 0.4))
    blob('cream', g, (0.04, 0.03, 0.31), (0.105, 0.105, 0.07), C('#fffaf3', 0.5), seg=18, ring=10)
    strawberry(g, 'berry', (0.07, -0.06, 0.32), 0.7)
    strawberry(g, 'berry2', (-0.1, -0.1, 0.285), 0.5)
    blueberry(g, 'blue1', (0.13, 0.1, 0.285), 0.9)
    blueberry(g, 'blue2', (-0.12, 0.08, 0.285), 0.8)

# ---------- 🍬 strawberry macarons ----------
def one_macaron(g, name, loc, tilt, shell, cream, size=1.0, drizzle=False):
    """Two domed shells with a ruffled foot each, around a thick ring of cream."""
    m = node(name, g, loc)
    m.rotation_euler = tilt
    m.scale = (size, size, size)
    sm, cm = C(shell, 0.35), C(cream, 0.55)
    R_ = 0.19
    dome_up = [(0.0005, 0.085), (0.07, 0.083), (0.13, 0.073), (0.17, 0.054), (0.186, 0.03), (R_, 0.0), (0.0005, 0.0)]
    lathe(f'{name}_top', m, (0, 0, 0.1), dome_up, sm, seg=56)
    lathe(f'{name}_bot', m, (0, 0, 0.05), [(r, -z * 0.8) for r, z in dome_up][::-1], sm, seg=56)
    # the cream sits between them, bulging out round the edge
    blob(f'{name}_cream', m, (0, 0, 0.075), (R_ * 1.04, R_ * 1.04, 0.036), cm, seg=48, ring=12)
    # the frilly "feet": one wavy ruffle just under each shell's rim
    for z0, nm in ((0.105, 'top'), (0.047, 'bot')):
        f = lathe(f'{name}_foot_{nm}', m, (0, 0, z0), [(R_ - 0.025, 0.014), (R_ + 0.012, 0.012), (R_ + 0.024, 0.0), (R_ + 0.012, -0.012), (R_ - 0.025, -0.014)], sm, seg=72)
        for v in f.data.vertices:
            a_ = math.atan2(v.co.y, v.co.x); k = 1 + 0.05 * math.sin(a_ * 22) * (v.co.x ** 2 + v.co.y ** 2 > 0.03)
            v.co.x *= k; v.co.y *= k
        for p in f.data.polygons: p.use_smooth = True
    if drizzle:   # a zigzag of white chocolate across the top shell
        zig = [((-1) ** k * 0.11, -0.14 + 0.056 * k, 0.172) for k in range(6)]
        tube(f'{name}_drizzle', m, [(x, y, 0.1 + 0.07 * math.sqrt(max(0.0, 1 - (x * x + y * y) / 0.036))) for x, y, _ in zig], [1] * 6, C('#fffaf3', 0.4), bevel=0.008)
    return m

@dessert
def macaron(g):
    one_macaron(g, 'm_back', (0.12, 0.08, 0.04), (0.5, 0.0, 0.5), '#9fe0bd', '#fff6ea', 0.95)
    one_macaron(g, 'm_side', (-0.17, 0.02, 0.04), (-0.45, 0.0, -0.3), '#bda3f4', '#fff6ea', 0.92)
    one_macaron(g, 'm_front', (0.0, -0.17, 0.0), (0.0, 0.0, 0.2), '#f78db1', '#fff1e6', 1.05, drizzle=True)
    strawberry(g, 'berry', (0.2, -0.17, 0.0), 0.55)
    blueberry(g, 'blue', (0.28, -0.04, 0.0), 0.8)

# ---------- 🍯 honey toast ----------
@dessert
def honeytoast(g):
    # a thick, square block of toast: a golden crust round a soft crumb, the top toasted brown
    rbox('crust', g, (0.4, 0.27, 0.4), (0, 0.135, 0), C('#dc9040', 0.75), r=0.05)
    rbox('crumb', g, (0.36, 0.02, 0.36), (0, 0.268, 0), C('#f6d79a', 0.7), r=0.008)
    # the top is cut into a crosshatch of little toasty cubes (rbox takes three.js coordinates: x, up, z)
    for i in range(3):
        for j in range(3):
            rbox(f'cube_{i}_{j}', g, (0.1, 0.05, 0.1), ((i - 1) * 0.115, 0.29, (j - 1) * 0.115), C('#f0b055' if (i + j) % 2 else '#f6c26a', 0.6), r=0.02)
    # honey: a glossy pool over the cubes, running down every side
    blob('honey', g, (0, 0, 0.318), (0.17, 0.17, 0.014), C('#ffc43a', 0.12), seg=28, ring=8)
    rnd = random.Random(11)
    for k in range(9):
        side, t = k % 4, rnd.uniform(-0.15, 0.15)
        x, y = [(t, -0.205), (0.205, t), (t, 0.205), (-0.205, t)][side]
        ln = 0.05 + rnd.random() * 0.08
        blob(f'drip_{k}', g, (x, y, 0.29 - ln * 0.5), (0.02, 0.02, ln * 0.5 + 0.015), C('#ffc43a', 0.15), seg=10, ring=8)
        blob(f'drip_tip_{k}', g, (x, y, 0.29 - ln), (0.024,) * 3, C('#ffc43a', 0.15), seg=10, ring=6)
    blob('butter', g, (-0.07, 0.07, 0.34), (0.065, 0.06, 0.025), C('#ffe27a', 0.4), rot=(0, 0, 0.5))
    # a scoop of vanilla ice cream with a swirl of cream, and a strawberry
    blob('scoop', g, (0.05, -0.02, 0.385), (0.1, 0.1, 0.085), C('#fff6e0', 0.5), seg=24, ring=14)
    blob('cream', g, (0.05, -0.02, 0.47), (0.055, 0.055, 0.045), C('#fffaf3', 0.5), seg=16, ring=10)
    strawberry(g, 'berry', (0.05, -0.02, 0.48), 0.6)
    strawberry(g, 'berry2', (-0.12, -0.12, 0.31), 0.5)
    blueberry(g, 'blue1', (0.13, 0.08, 0.31), 0.9)
    blueberry(g, 'blue2', (0.15, -0.05, 0.31), 0.8)
    mint(g, 'mint', (0.08, -0.1, 0.5), 0.9, 0.5)

# ---------- 🍮 custard pudding ----------
@dessert
def pudding(g):
    # a pool of caramel on the plate, where the pudding was turned out
    blob('pool', g, (0, 0, 0.006), (0.25, 0.25, 0.008), C('#cf7524', 0.15), seg=32, ring=8)
    # the custard: a soft frustum, wider at the foot, its top shoulder rounded
    lathe('custard', g, (0, 0, 0), [(0.0005, 0.25), (0.13, 0.25), (0.155, 0.235), (0.168, 0.21), (0.2, 0.02), (0.205, 0.0), (0.0005, 0.0)], C('#ffd95a', 0.4), seg=64)
    # the caramel top, and caramel running down the sides
    lathe('caramel', g, (0, 0, 0), [(0.0005, 0.262), (0.12, 0.26), (0.155, 0.248), (0.172, 0.225), (0.176, 0.205), (0.0005, 0.205)], C('#c26a1e', 0.12), seg=64)
    rnd = random.Random(5)
    for k in range(7):
        a = k / 7 * 2 * math.pi + rnd.uniform(-0.15, 0.15); ln = 0.035 + rnd.random() * 0.06
        r = 0.172 + 0.032 * (ln * 0.5 + 0.02) / 0.21
        blob(f'drip_{k}', g, (math.cos(a) * r, math.sin(a) * r, 0.215 - ln * 0.5), (0.016, 0.016, ln * 0.5 + 0.012), C('#c26a1e', 0.12), seg=10, ring=8)
        rr = 0.172 + 0.032 * (ln + 0.02) / 0.21
        blob(f'drip_tip_{k}', g, (math.cos(a) * rr, math.sin(a) * rr, 0.215 - ln), (0.019,) * 3, C('#c26a1e', 0.12), seg=10, ring=6)
    # a swirl of cream and a strawberry on top
    blob('cream', g, (0, 0, 0.29), (0.07, 0.07, 0.04), C('#fffaf0', 0.5), seg=20, ring=12)
    blob('cream2', g, (0, 0, 0.325), (0.045, 0.045, 0.03), C('#fffaf0', 0.5), seg=16, ring=10)
    strawberry(g, 'berry', (0.0, 0.0, 0.33), 0.55)
    blob('shine', g, (-0.1, -0.15, 0.13), (0.012, 0.008, 0.07), C('#fffbe8', 0.3), rot=(0, 0.25, 0.5), seg=10, ring=8)   # a glossy streak down the custard
    mint(g, 'mint', (0.15, -0.17, 0.025), 1.0, 0.6)

# ---------- 🍧 snow bingsu ----------
@dessert
def bingsu(g):
    # a white bowl on a little foot, with a pink band round the rim
    lathe('bowl', g, (0, 0, 0), [(0.0005, 0.0), (0.1, 0.0), (0.11, 0.018), (0.2, 0.06), (0.245, 0.13), (0.25, 0.145), (0.24, 0.148), (0.232, 0.135), (0.19, 0.075), (0.0005, 0.05)], C('#fffaf3', 0.3), seg=64)
    lathe('band', g, (0, 0, 0), [(0.247, 0.142), (0.251, 0.148), (0.242, 0.122), (0.238, 0.118)], C('#ff9fbf', 0.4), seg=64)
    # the snow: a soft mound of shaved milk, rough with flakes
    lathe('snow', g, (0, 0, 0), [(0.0005, 0.39), (0.06, 0.385), (0.12, 0.35), (0.17, 0.29), (0.215, 0.2), (0.235, 0.14), (0.0005, 0.12)], C('#fbf7f2', 0.9), seg=48)
    rnd = random.Random(11)
    for k in range(40):
        a = rnd.uniform(0, 2 * math.pi); h = rnd.uniform(0.0, 1.0)
        r = 0.23 * (1 - h) ** 0.8 + 0.02; z = 0.14 + 0.25 * (1 - (1 - h) ** 1.6)
        blob(f'flake_{k}', g, (math.cos(a) * r, math.sin(a) * r, z), (0.022, 0.022, 0.009), C('#ffffff', 0.95), rot=(rnd.uniform(-0.6, 0.6), rnd.uniform(-0.6, 0.6), a), seg=6, ring=4)
    # condensed milk poured over the top, running down the snow in thick drips
    blob('milk_top', g, (0, 0, 0.385), (0.1, 0.1, 0.02), C('#fff0c8', 0.15), seg=24, ring=10)
    prof = [(0.0, 0.39), (0.06, 0.385), (0.12, 0.35), (0.17, 0.29), (0.215, 0.2), (0.235, 0.14)]
    def surf(r):   # the height of the snow at radius r
        for (r0, z0), (r1, z1) in zip(prof, prof[1:]):
            if r <= r1: return z0 + (z1 - z0) * (r - r0) / (r1 - r0)
        return prof[-1][1]
    for k in range(10):
        a = k / 10 * 2 * math.pi + rnd.uniform(-0.2, 0.2); end = rnd.uniform(0.15, 0.2); n = 9
        for j in range(n + 1):
            r = 0.08 + (end - 0.08) * j / n; th = 0.019 + 0.006 * (j == n)
            blob(f'milk_{k}_{j}', g, (math.cos(a) * r, math.sin(a) * r, surf(r) + 0.006), (th, th, th * 0.8), C('#fff0c8', 0.15), seg=8, ring=5)
    # strawberries tucked round the mound, and a scoop of strawberry ice cream on top with one more
    for k in range(5):
        a = k / 5 * 2 * math.pi + 0.3
        strawberry(g, f'berry_{k}', (math.cos(a) * 0.2, math.sin(a) * 0.2, 0.14), 0.55)
    blob('scoop', g, (0, 0, 0.43), (0.075, 0.075, 0.06), C('#ffb3cc', 0.6), seg=20, ring=12)
    for k in range(8):
        a = k / 8 * 2 * math.pi
        blob(f'scoop_lip_{k}', g, (math.cos(a) * 0.07, math.sin(a) * 0.07, 0.405), (0.022, 0.022, 0.016), C('#ffb3cc', 0.6), seg=8, ring=6)
    strawberry(g, 'berry_top', (0.0, 0.0, 0.47), 0.6)

# ---------- 🎂 festival cake ----------
@dessert
def festivalcake(g):
    # a plate, then three tiers (pink, vanilla, lilac) that get smaller going up, each with a cream cap and a ring of piped beads
    cyl('plate', g, 0.3, 0.27, 0.025, (0, 0, 0.0125), C('#ffffff', 0.3), r=0.008, seg=48)
    tiers = [(0.22, 0.12, '#ffc4d6', '#fffaf0'), (0.16, 0.11, '#fff2dc', '#ffd1e0'), (0.105, 0.1, '#d8c4ff', '#fffaf0')]
    z = 0.025
    rnd = random.Random(5)
    tops = []
    for k, (r, h, col, cap) in enumerate(tiers):
        cyl(f'tier_{k}', g, r, r, h, (0, 0, z + h / 2), C(col, 0.7), r=0.012, seg=48)
        cyl(f'cap_{k}', g, r + 0.004, r + 0.004, 0.018, (0, 0, z + h + 0.004), C(cap, 0.45), r=0.007, seg=48)
        for j in range(16 + 4 * (2 - k)):   # drips of cream down the side, and piped beads round the foot
            a = j / (16 + 4 * (2 - k)) * 2 * math.pi
            blob(f'bead_{k}_{j}', g, (math.cos(a) * (r + 0.002), math.sin(a) * (r + 0.002), z + 0.012), (0.014, 0.014, 0.011), C('#ffffff', 0.4), seg=8, ring=6)
            if j % 2 == 0:
                ln = rnd.uniform(0.02, 0.05)
                blob(f'drip_{k}_{j}', g, (math.cos(a) * (r + 0.001), math.sin(a) * (r + 0.001), z + h - ln / 2 + 0.005), (0.012, 0.012, ln / 2), C(cap, 0.4), seg=8, ring=6)
        for j in range(5 + k):   # sprinkles stuck on the side
            a = rnd.uniform(0, 2 * math.pi); zz = z + rnd.uniform(0.03, h - 0.03)
            blob(f'sprinkle_{k}_{j}', g, (math.cos(a) * (r + 0.003), math.sin(a) * (r + 0.003), zz), (0.012, 0.004, 0.004), C(['#ff7ea6', '#ffd54a', '#7fd6c2', '#9b8cff'][j % 4]), rot=(0, 0, a + 1.57), seg=6, ring=4)
        tops.append(z + h + 0.013)
        z += h
    # strawberries round the middle cap, a mound of cream on the top one
    for j in range(7):
        a = j / 7 * 2 * math.pi + 0.2
        strawberry(g, f'berry_{j}', (math.cos(a) * 0.15, math.sin(a) * 0.15, tops[1]), 0.5)
    blob('cream', g, (0, 0, tops[2] + 0.012), (0.05, 0.05, 0.03), C('#fffaf0', 0.45), seg=20, ring=10)
    strawberry(g, 'berry_top', (0.0, 0.0, tops[2] + 0.02), 0.5)
    # three sparklers and a golden star on a stick, so it looks like a party
    for j, a in enumerate((0.9, 2.9, 5.0)):
        x, y = math.cos(a) * 0.065, math.sin(a) * 0.065
        cyl(f'candle_{j}', g, 0.007, 0.007, 0.07, (x, y, tops[2] + 0.055), C(['#ff7ea6', '#7fd6c2', '#ffd54a'][j], 0.5), r=0.003, seg=10)
        for m in range(6):
            b = m / 6 * 2 * math.pi
            blob(f'spark_{j}_{m}', g, (x + math.cos(b) * 0.014, y + math.sin(b) * 0.014, tops[2] + 0.1 + 0.012 * (m % 2)), (0.004, 0.004, 0.016), C('#ffd54a', 0.3), rot=(math.cos(b) * 0.7, math.sin(b) * 0.7, 0), seg=6, ring=4)
    cyl('stick', g, 0.004, 0.004, 0.1, (0.0, 0.0, tops[2] + 0.1), C('#e8b886', 0.6), r=0.002, seg=8)
    for m in range(5):   # a star made of five points
        b = m / 5 * 2 * math.pi + math.pi / 2
        blob(f'star_{m}', g, (math.cos(b) * 0.026, 0.0, tops[2] + 0.17 + math.sin(b) * 0.026), (0.016, 0.006, 0.016), C('#ffd54a', 0.25), rot=(0, b, 0), seg=8, ring=6)
    blob('star_mid', g, (0.0, 0.0, tops[2] + 0.17), (0.022, 0.008, 0.022), C('#ffd54a', 0.25), seg=10, ring=8)
    # little bunting flags across the plate's front
    for j in range(5):
        x = -0.2 + j * 0.1
        blob(f'flag_{j}', g, (x, -0.27 + 0.04 * abs(j - 2) * 0, 0.045 + 0.03 * (1 - abs(j - 2) / 2.0)), (0.026, 0.004, 0.028), C(['#ff7ea6', '#ffd54a', '#7fd6c2', '#9b8cff', '#ff9f6b'][j], 0.5), rot=(0, 0, 0), seg=8, ring=6)

# ---------- 🍵 matcha roll ----------
@dessert
def matcharoll(g):
    # a slice of the roll stands on its edge, so the spiral faces the front: a green sponge with a darker skin
    R0, D, Z = 0.19, 0.14, 0.19
    cyl('skin', g, R0 + 0.004, R0 + 0.004, D - 0.012, (0, Z, 0), C('#7fa64c', 0.75), r=0.02, rot=(math.pi / 2, 0, 0), seg=40)
    cyl('sponge', g, R0, R0, D, (0, Z, 0), C('#a9cc6e', 0.8), r=0.012, rot=(math.pi / 2, 0, 0), seg=40)
    # the cream rolled up inside: a spiral band through the slice, standing just proud of both cut faces
    bm = bmesh.new(); N, turns, w, y0 = 90, 2.3, 0.02, D / 2 + 0.003
    rows = []
    for i in range(N + 1):
        t = i / N; a = t * turns * 2 * math.pi + 0.6; r = 0.025 + t * 0.14
        ca, sa = math.cos(a), math.sin(a)
        rows.append([bm.verts.new((rr * ca, y, Z + rr * sa)) for rr, y in ((r, -y0), (r + w, -y0), (r + w, y0), (r, y0))])
    for a, b in zip(rows, rows[1:]):
        for k in range(4):
            bm.faces.new((a[k], a[(k + 1) % 4], b[(k + 1) % 4], b[k]))
    bm.faces.new(rows[0]); bm.faces.new(list(reversed(rows[-1])))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    _mesh_object('spiral', g, (0, 0, 0), bm, C('#fffaf0', 0.55))
    # a swirl of whipped cream on top, dusted with matcha, and a strawberry
    blob('cream', g, (0, 0, Z + R0 + 0.025), (0.075, 0.06, 0.045), C('#fffaf0', 0.5), seg=20, ring=12)
    blob('cream2', g, (0, 0, Z + R0 + 0.06), (0.045, 0.04, 0.03), C('#fffaf0', 0.5), seg=16, ring=10)
    strawberry(g, 'berry', (0.01, 0.0, Z + R0 + 0.065), 0.55)
    rnd = random.Random(7)
    for k in range(10):
        a = rnd.uniform(0, 2 * math.pi); rr = rnd.uniform(0.03, 0.07)
        blob(f'dust_{k}', g, (math.cos(a) * rr, math.sin(a) * rr * 0.8, Z + R0 + 0.045 + rnd.uniform(0, 0.015)), (0.008,) * 3, C('#6f9a3a'), seg=6, ring=4)
    # two sweet red beans by its foot
    for k, x in enumerate((-0.14, 0.15)):
        blob(f'bean_{k}', g, (x, -0.1, 0.02), (0.022, 0.016, 0.016), C('#7a2b2b', 0.3), seg=10, ring=6)

root = scenery(WHO)
BUILT[WHO](root)
finish(reach=0.15, view='auto', strength=0.4, join=root)
