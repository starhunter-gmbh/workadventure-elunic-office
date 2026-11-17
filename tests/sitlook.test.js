// Logic test of the sitting look in newoffice-script.js: runs the real map script against a stubbed WA API.
// Run: node tests/sitlook.test.js   (exit code 1 on failure)
const fs = require("fs");
const path = require("path");
const vm = require("vm");
const assert = require("assert");

const src = fs.readFileSync(path.join(__dirname, "..", "newoffice-script.js"), "utf8");
const chair = /\[(\d+), (\d+), "(\w+)"\]/.exec(src.split("const CHAIRS = ")[1]).slice(1, 4);
const CX = Number(chair[0]), CY = Number(chair[1]);

function run({ remoteSitting = [] } = {}) {
    const posted = [], saved = [], timers = [];
    let pos = { x: 0, y: 0 };
    let moveCb;
    const noop = new Proxy(function () {}, {
        get: (t, k) => (k === "then" ? undefined : k === Symbol.toPrimitive ? () => "" : noop),
        apply: () => noop,
    });
    const sub = (fn) => ({ subscribe: fn || (() => {}) });
    const players = remoteSitting.map((id) => ({ playerId: id, position: { x: 0, y: 0 }, state: { elunicSit: true } }));
    const soft = (o) => new Proxy(o, { get: (t, k) => (k in t ? t[k] : noop) });
    const WA = soft({
        onInit: () => Promise.resolve(),
        player: soft({
            state: soft({ saveVariable: (k, v, o) => { saved.push([k, v, o]); return Promise.resolve(); } }),
            onPlayerMove: (cb) => { moveCb = cb; },
            getPosition: async () => ({ x: pos.x, y: pos.y }),
            teleport: () => Promise.resolve(),
            playerId: 1,
        }),
        players: soft({
            configureTracking: () => Promise.resolve(),
            list: () => players[Symbol.iterator](),
            onVariableChange: () => sub(), onPlayerEnters: sub(), onPlayerLeaves: sub(),
        }),
        room: soft({ mapURL: "http://x/elunic-office.wam", hashParameters: {} }),
    });
    const window = {
        parent: { postMessage: (m) => posted.push(m) }, top: null,
        addEventListener: () => {}, navigator: { language: "de" },
    };
    window.top = window.parent;
    const ctx = vm.createContext({
        WA, window, console: { info() {}, warn() {}, log() {} },
        setInterval: (fn, ms) => { timers.push(fn); return timers.length; }, setTimeout: () => 0, clearTimeout() {},
        fetch: () => Promise.reject(new Error("no net")), URL, navigator: window.navigator, Date, Math, Promise,
        document: noop, encodeURIComponent, JSON, Object, Array, Map, Set, Number, String,
    });
    vm.runInContext(src, ctx);
    return { posted, saved, timers, move: (ev) => moveCb(ev), setPos: (x, y) => { pos = { x, y }; }, poll: () => Promise.all(timers.map((f) => f())) };
}
const tick = () => new Promise((r) => setImmediate(r));
const lastLook = (t) => t.posted.filter((m) => m.type === "elunic-sitlook").pop();

(async () => {
    const t = run({ remoteSitting: [7, 9] });
    await tick(); await tick();
    assert(t.move, "chair block did not register onPlayerMove");

    // walking past: no sitting
    t.move({ x: CX + 60, y: CY, moving: true, direction: "left" });
    assert.strictEqual(t.saved.length, 0, "moving must not sit");

    // stopped exactly on the chair centre (end of the snap walk): sits, public variable, bridge message
    t.move({ x: CX, y: CY, moving: false, direction: "left" });
    assert.strictEqual(JSON.stringify(t.saved), JSON.stringify([["elunicSit", true, { public: true, persist: false, scope: "room" }]]));
    assert.strictEqual(JSON.stringify(lastLook(t)), JSON.stringify({ type: "elunic-sitlook", self: true, players: [7, 9] }));

    // a tiny jitter right after the stop does not stand up; moving beyond 4 px does
    t.move({ x: CX + 2, y: CY, moving: true, direction: "left" });
    assert.strictEqual(t.saved.length, 1, "2 px of movement must not stand up");
    t.move({ x: CX + 9, y: CY, moving: true, direction: "left" });
    assert.strictEqual(t.saved.length, 2);
    assert.strictEqual(JSON.stringify(t.saved[1].slice(0, 2)), JSON.stringify(["elunicSit", false]));
    assert.strictEqual(lastLook(t).self, false);

    // stopping 15 px away from the chair: the snap walks on, but until then nobody sits
    t.move({ x: CX + 15, y: CY, moving: false, direction: "left" });
    assert.strictEqual(t.saved.length, 2);

    // teleport onto a chair (no move event): the poll finds it (position unchanged between two polls)
    const t2 = run();
    await tick(); await tick();
    t2.setPos(CX, CY);
    await t2.poll();                       // first poll, no earlier position known: resting on a chair centre = sits
    assert.strictEqual(t2.saved.length, 1, "teleport/spawn onto a chair must sit");
    assert.strictEqual(lastLook(t2).self, true);
    await t2.poll();                       // unchanged: stays
    assert.strictEqual(t2.saved.length, 1);
    t2.setPos(CX + 80, CY + 40);           // teleported away (calendar meeting): position changed, far from the seat
    await t2.poll();
    assert.strictEqual(t2.saved.length, 2, "teleport away must stand up");
    assert.strictEqual(lastLook(t2).self, false);
    t2.setPos(CX + 80, CY + 40);           // resting somewhere that is no chair: stays standing
    await t2.poll();
    assert.strictEqual(t2.saved.length, 2);
    console.log("ok: sit on stop, stand on move, no sit while walking, remote sitters passed on");
})().catch((e) => { console.error("FAIL", e); process.exit(1); });
