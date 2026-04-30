"use strict";

/*
  Echo Escape V4.2 - Minimal Low-Spec + Reliable Monster Chase

  Changes:
  - Very simple visuals: black background, white probe balls, white lines.
  - No heavy glow, no scanlines, no large particle system.
  - Fewer probes and capped active probes.
  - Strong probes wake monsters reliably.
  - Soft rapid probes do NOT wake monsters.
  - Monsters use grid pathfinding to chase the player instead of simple straight-line movement.
*/

(function () {
  const TILE = 32;
  const ROWS = 20;
  const COLS = 30;
  const WORLD_W = COLS * TILE;
  const WORLD_H = ROWS * TILE;

  let canvas = null;
  let ctx = null;

  const LEVELS = [
    {
      id: 1,
      name: "First Signal",
      difficulty: "Easy",
      map: [
        "##############################",
        "#S...........#...............#",
        "#.######.###.#.########.####.#",
        "#......#.#...#........#....#.#",
        "######.#.#.##########.####.#.#",
        "#......#.#......#........#.#.#",
        "#.######.######.#.######.#.#.#",
        "#..............#.#....#..#...#",
        "#.##############.#.##.#.######",
        "#.......#........#.#..#......#",
        "#######.#.########.#.#######.#",
        "#.......#......#...#.....^...#",
        "#.############.#.###########.#",
        "#......^.......#.............#",
        "#.###########.###########.####",
        "#.#.........#.........#......#",
        "#.#.#######.#########.#.####.#",
        "#...#.................#....E.#",
        "#.##########################.#",
        "##############################"
      ]
    },
    {
      id: 2,
      name: "Cold Corridor",
      difficulty: "Easy",
      map: [
        "##############################",
        "#S..........#................#",
        "###########.#.##############.#",
        "#...........#......^.........#",
        "#.##########################.#",
        "#.#..........................#",
        "#.#.##########################",
        "#.#.#.......................E#",
        "#.#.#.######################.#",
        "#.#.#..........#.............#",
        "#.#.##########.#.#############",
        "#.#............#.............#",
        "#.##########################.#",
        "#..............^.............#",
        "############.#################",
        "#............#...............#",
        "#.############.#############.#",
        "#............................#",
        "#.##########################.#",
        "##############################"
      ]
    },
    {
      id: 3,
      name: "Broken Chapel",
      difficulty: "Normal",
      map: [
        "##############################",
        "#S........#.................^#",
        "#.######.#.#################.#",
        "#......#.#.#.................#",
        "######.#.#.#.###############.#",
        "#......#...#.#...............#",
        "#.##########.#.###############",
        "#............#...............#",
        "#.##########################.#",
        "#...............^............#",
        "############################.#",
        "#............................#",
        "#.############################",
        "#..............#.............#",
        "#.############.#.###########.#",
        "#.#............#.#...........#",
        "#.#.############.#.#########.#",
        "#.#.........................E#",
        "#.##########################.#",
        "##############################"
      ]
    },
    {
      id: 4,
      name: "Quiet Machinery",
      difficulty: "Normal",
      map: [
        "##############################",
        "#S..........#...............E#",
        "#.#########.#.##############.#",
        "#.....#.....#..........^.....#",
        "#####.#.###############.######",
        "#.....#.................#....#",
        "#.############.##########.##.#",
        "#............#............##.#",
        "###########.###############..#",
        "#.........#.................##",
        "#.#######.#################..#",
        "#.#.....#.......^...........##",
        "#.#.###.###############.######",
        "#...#.#...............#......#",
        "#####.###############.######.#",
        "#.................#..........#",
        "#.###############.#.##########",
        "#.................#..........#",
        "#.##########################.#",
        "##############################"
      ]
    },
    {
      id: 5,
      name: "Flooded Memory",
      difficulty: "Normal",
      map: [
        "##############################",
        "#S..............#...........E#",
        "#.#############.#.##########.#",
        "#.......#.......#......^.....#",
        "#######.#.#############.######",
        "#.......#.....#.........#....#",
        "#.###########.#.#########.##.#",
        "#.............#...........##.#",
        "#.##########################.#",
        "#...........^................#",
        "###########################.##",
        "#............................#",
        "#.############################",
        "#.#.........................^#",
        "#.#.########################.#",
        "#.#..........................#",
        "#.##########################.#",
        "#............................#",
        "#.##########################.#",
        "##############################"
      ]
    },
    {
      id: 6,
      name: "Glass Spine",
      difficulty: "Hard",
      map: [
        "##############################",
        "#S........#.................E#",
        "#.######.#.#################.#",
        "#.#....#.#.................#.#",
        "#.#.##.#.###############.#.#.#",
        "#.#.##.#.................#.#.#",
        "#.#.##.###################.#.#",
        "#.#.##.....................#.#",
        "#.#.#######################.#.",
        "#.#.........................#.",
        "#.###########################.",
        "#..............^............#.",
        "###########################.#.",
        "#...........................#.",
        "#.###########################.",
        "#.#.........................#.",
        "#.#.#########################.",
        "#.#.........................^#",
        "#.##########################.#",
        "##############################"
      ]
    },
    {
      id: 7,
      name: "Red Static",
      difficulty: "Hard",
      map: [
        "##############################",
        "#S.....#.................#...#",
        "#####.#.###############.#.#.##",
        "#.....#.......#.........#.#E##",
        "#.###########.#.#########.#.##",
        "#.#...........#.......^...#.##",
        "#.#.#######################.##",
        "#.#.........................##",
        "#.###########################",
        "#...........................#",
        "###########################.#",
        "#.............^.............#",
        "#.###########################",
        "#.#.........................#",
        "#.#.#######################.#",
        "#.#.#.....................#.#",
        "#.#.#.###################.#.#",
        "#...#.....................#.#",
        "#.#########################.#",
        "##############################"
      ]
    },
    {
      id: 8,
      name: "Lower Archive",
      difficulty: "Hard",
      map: [
        "##############################",
        "#S...........................#",
        "#.##########################.#",
        "#.#........................#.#",
        "#.#.######################.#.#",
        "#.#.#....................#.#.#",
        "#.#.#.##################.#.#.#",
        "#.#.#.#................#.#.#.#",
        "#.#.#.#.##############.#.#.#.#",
        "#.#.#.#.#......^.....#.#.#.#.#",
        "#.#.#.#.############.#.#.#.#.#",
        "#.#.#.#..............#.#.#.#.#",
        "#.#.#.################.#.#.#.#",
        "#.#.#..................#.#.#.#",
        "#.#.####################.#.#.#",
        "#.#......................#.#.#",
        "#.########################.#.#",
        "#..........................#E#",
        "#.##########################.#",
        "##############################"
      ]
    },
    {
      id: 9,
      name: "Black Garden",
      difficulty: "Expert",
      map: [
        "##############################",
        "#S............#..............#",
        "#.###########.#.############.#",
        "#.....^.......#..............#",
        "#############.##############.#",
        "#............................#",
        "#.##########################.#",
        "#.#........................#.#",
        "#.#.######################.#.#",
        "#.#.#....................#.#.#",
        "#.#.#.##################.#.#.#",
        "#.#.#..............^.....#.#.#",
        "#.#.######################.#.#",
        "#.#........................#.#",
        "#.##########################.#",
        "#.....................^......#",
        "############################.#",
        "#...........................E#",
        "#.##########################.#",
        "##############################"
      ]
    },
    {
      id: 10,
      name: "Signal Nest",
      difficulty: "Expert",
      map: [
        "##############################",
        "#S..........#...............^#",
        "##########.#.#################",
        "#..........#.................#",
        "#.##########################.#",
        "#.#.....................^..#.#",
        "#.#.######################.#.#",
        "#.#.#....................#.#.#",
        "#.#.#.##################.#.#.#",
        "#.#.#.#................#.#.#.#",
        "#.#.#.#.##############.#.#.#.#",
        "#.#.#.#..............#.#.#.#.#",
        "#.#.#.################.#.#.#.#",
        "#.#.#..................#.#.#.#",
        "#.#.####################.#.#.#",
        "#.#......................#.#.#",
        "#.########################.#.#",
        "#..........................#E#",
        "#.##########################.#",
        "##############################"
      ]
    },
    {
      id: 11,
      name: "Deep Receiver",
      difficulty: "Expert",
      map: [
        "##############################",
        "#S...............#..........E#",
        "#.##############.#.#########.#",
        "#..............#.#.....^.....#",
        "##############.#.#############",
        "#..............#.............#",
        "#.##########################.#",
        "#.#..........................#",
        "#.#.##########################",
        "#.#.#........................#",
        "#.#.#.######################.#",
        "#.#.#............^.........#.#",
        "#.#.######################.#.#",
        "#.#........................#.#",
        "#.##########################.#",
        "#............................#",
        "#.##########################.#",
        "#..........^.................#",
        "#.##########################.#",
        "##############################"
      ]
    },
    {
      id: 12,
      name: "Final Frequency",
      difficulty: "Final",
      map: [
        "##############################",
        "#S...........................#",
        "#.##########################.#",
        "#.#..............^.........#.#",
        "#.#.######################.#.#",
        "#.#.#....................#.#.#",
        "#.#.#.##################.#.#.#",
        "#.#.#.#................#.#.#.#",
        "#.#.#.#.##############.#.#.#.#",
        "#.#.#.#.#............#.#.#.#.#",
        "#.#.#.#.#.##########.#.#.#.#.#",
        "#.#.#.#.#......^...#.#.#.#.#.#",
        "#.#.#.#.############.#.#.#.#.#",
        "#.#.#.#..............#.#.#.#.#",
        "#.#.#.################.#.#.#.#",
        "#.#.#..................#.#.#.#",
        "#.#.####################.#.#.#",
        "#.#......................#.#E#",
        "#.##########################.#",
        "##############################"
      ]
    }
  ];

  const state = {
    scale: 1,
    currentLevel: 0,
    mode: "menu",
    grid: [],
    reveal: [],
    memory: [],
    keys: new Set(),
    probes: [],
    monsters: [],
    serverSummary: null,
    player: {
      x: 64,
      y: 64,
      vx: 0,
      vy: 0,
      radius: 9,
      maxSpeed: 160,
      accel: 980,
      friction: 0.84
    },
    startAt: 0,
    elapsed: 0,
    echoCount: 0,
    stealthCount: 0,
    deathCount: 0,
    lastStepProbe: 0,
    lastManualProbe: 0,
    resultSubmitted: false,
    fpsFrames: 0,
    fpsTime: 0,
    fpsTotal: 0
  };

  const el = {};

  function getElements() {
    const ids = [
      "game", "overlay", "overlayTitle", "overlayText", "startBtn", "levelBtn",
      "levelSelect", "levelStat", "difficultyStat", "timeStat", "echoStat",
      "statusStat", "hintStat", "savedStat", "fpsLabel", "missionTitle",
      "missionSubtitle", "levelBest", "summaryWins", "summaryLosses", "summaryBest"
    ];

    for (const id of ids) {
      el[id] = document.getElementById(id);
    }

    canvas = el.game;
    if (!canvas) throw new Error("Canvas element with id='game' was not found.");

    ctx = canvas.getContext("2d", { alpha: false });
    if (!ctx) throw new Error("Canvas 2D context is not available.");
  }

  function safeText(element, text) {
    if (element) element.textContent = text;
  }

  function showFatalError(error) {
    console.error(error);
    const overlay = document.getElementById("overlay");
    const title = document.getElementById("overlayTitle");
    const text = document.getElementById("overlayText");
    if (title) title.textContent = "Game Error";
    if (text) text.textContent = "The game script hit an error: " + (error && error.message ? error.message : String(error));
    if (overlay) overlay.classList.add("show");
  }

  function csrfToken() {
    const meta = document.querySelector("meta[name='csrf-token']");
    return meta ? meta.getAttribute("content") : "";
  }

  function normaliseRows(rows) {
    const output = [];
    for (let y = 0; y < ROWS; y++) {
      let row = rows[y] || "";
      if (row.length > COLS) row = row.slice(0, COLS);
      if (row.length < COLS) row = row.padEnd(COLS, "#");
      output.push(row);
    }
    return output;
  }

  function populateLevelSelect() {
    if (!el.levelSelect) return;
    el.levelSelect.innerHTML = "";
    LEVELS.forEach((level, index) => {
      const option = document.createElement("option");
      option.value = String(index);
      option.textContent = `Level ${level.id} · ${level.name} · ${level.difficulty}`;
      el.levelSelect.appendChild(option);
    });
  }

  async function loadSummary() {
    try {
      const response = await fetch("/api/me/summary");
      if (!response.ok) return;
      const data = await response.json();
      if (!data.ok) return;

      state.serverSummary = data;
      safeText(el.summaryWins, data.wins);
      safeText(el.summaryLosses, data.losses);
      safeText(el.summaryBest, data.best_score || "--");
      updateLevelBest();
    } catch (err) {
      console.warn("Summary unavailable", err);
    }
  }

  function updateLevelBest() {
    if (!el.levelBest) return;

    if (!state.serverSummary || !state.serverSummary.best_by_level) {
      el.levelBest.textContent = "Best: --";
      return;
    }

    const levelNumber = String(state.currentLevel + 1);
    const best = state.serverSummary.best_by_level[levelNumber];

    if (!best) {
      el.levelBest.textContent = "Best: --";
    } else {
      el.levelBest.textContent = `Best: ${best.score} pts · ${Number(best.time_seconds).toFixed(1)}s · ${best.echo_count} echoes`;
    }
  }

  async function submitResult(resultValue) {
    if (state.resultSubmitted) return;
    state.resultSubmitted = true;
    safeText(el.savedStat, "Saving");

    try {
      const response = await fetch("/api/results", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": csrfToken()
        },
        body: JSON.stringify({
          level: state.currentLevel + 1,
          result: resultValue,
          time_seconds: Math.max(1.1, Number(state.elapsed.toFixed(2))),
          echo_count: state.echoCount + state.stealthCount,
          death_count: state.deathCount
        })
      });

      const data = await response.json();
      if (data.ok) {
        safeText(el.savedStat, String(data.score));
        await loadSummary();
      } else {
        safeText(el.savedStat, "Error");
        console.warn(data.error);
      }
    } catch (err) {
      safeText(el.savedStat, "Offline");
      console.error(err);
    }
  }

  function setupCanvas() {
    const rect = canvas.getBoundingClientRect();
    const cssW = Math.max(520, Math.floor(rect.width || 900));
    const cssH = Math.floor(cssW * 2 / 3);

    // Low-spec mode: DPR is intentionally 1.
    canvas.width = cssW;
    canvas.height = cssH;
    canvas.style.height = cssH + "px";
    state.scale = Math.min(canvas.width / WORLD_W, canvas.height / WORLD_H);
    if (!isFinite(state.scale) || state.scale <= 0) state.scale = 1;
  }

  function inBounds(tx, ty) {
    return tx >= 0 && tx < COLS && ty >= 0 && ty < ROWS;
  }

  function tileAt(tx, ty) {
    if (!inBounds(tx, ty)) return "#";
    return state.grid[ty][tx];
  }

  function tileAtPixel(px, py) {
    return tileAt(Math.floor(px / TILE), Math.floor(py / TILE));
  }

  function isWallTile(tx, ty) {
    return tileAt(tx, ty) === "#";
  }

  function isWallAtPixel(px, py) {
    return tileAtPixel(px, py) === "#";
  }

  function isPassable(tx, ty) {
    return inBounds(tx, ty) && tileAt(tx, ty) !== "#";
  }

  function revealTile(tx, ty, duration) {
    tx = Math.floor(tx);
    ty = Math.floor(ty);
    if (!inBounds(tx, ty)) return;
    const now = performance.now();
    state.reveal[ty][tx] = Math.max(state.reveal[ty][tx], now + duration);
    state.memory[ty][tx] = Math.max(state.memory[ty][tx], now + 5000);
  }

  function revealArea(px, py, radiusTiles, duration) {
    const radius = Math.ceil(radiusTiles);
    const cx = Math.floor(px / TILE);
    const cy = Math.floor(py / TILE);

    for (let y = cy - radius; y <= cy + radius; y++) {
      for (let x = cx - radius; x <= cx + radius; x++) {
        if (inBounds(x, y)) revealTile(x, y, duration);
      }
    }
  }

  function canMoveTo(nx, ny, radius) {
    const r = radius;
    const samples = [
      [nx - r, ny - r],
      [nx + r, ny - r],
      [nx - r, ny + r],
      [nx + r, ny + r],
      [nx, ny - r - 1],
      [nx, ny + r + 1],
      [nx - r - 1, ny],
      [nx + r + 1, ny]
    ];
    return samples.every(([x, y]) => !isWallAtPixel(x, y));
  }

  function nearestPassableTile(tx, ty) {
    if (isPassable(tx, ty)) return { tx, ty };

    for (let r = 1; r < 8; r++) {
      for (let y = ty - r; y <= ty + r; y++) {
        for (let x = tx - r; x <= tx + r; x++) {
          if (isPassable(x, y)) return { tx: x, ty: y };
        }
      }
    }
    return { tx: 1, ty: 1 };
  }

  function loadLevel(levelIndex) {
    const level = LEVELS[levelIndex] || LEVELS[0];

    state.currentLevel = Math.max(0, Math.min(levelIndex, LEVELS.length - 1));
    state.grid = normaliseRows(level.map).map(row => row.split(""));
    state.reveal = Array.from({ length: ROWS }, () => Array(COLS).fill(0));
    state.memory = Array.from({ length: ROWS }, () => Array(COLS).fill(0));
    state.probes = [];
    state.monsters = [];
    state.echoCount = 0;
    state.stealthCount = 0;
    state.deathCount = 0;
    state.elapsed = 0;
    state.resultSubmitted = false;
    state.mode = "playing";
    state.startAt = performance.now();
    safeText(el.savedStat, "--");

    let foundStart = false;
    for (let y = 0; y < ROWS; y++) {
      for (let x = 0; x < COLS; x++) {
        if (state.grid[y][x] === "S") {
          state.player.x = x * TILE + TILE / 2;
          state.player.y = y * TILE + TILE / 2;
          state.grid[y][x] = ".";
          foundStart = true;
        }
      }
    }

    if (!foundStart) {
      state.player.x = TILE * 1.5;
      state.player.y = TILE * 1.5;
    }

    state.player.vx = 0;
    state.player.vy = 0;

    const monsterData = level.monsters || [];
    state.monsters = monsterData.map((m, index) => {
      const fixed = nearestPassableTile(m.x, m.y);
      return {
        id: index,
        x: fixed.tx * TILE + TILE / 2,
        y: fixed.ty * TILE + TILE / 2,
        r: 10,
        speed: state.player.maxSpeed,
        state: "sleep",
        revealUntil: performance.now() + 1800,
        path: [],
        pathTimer: 0
      };
    });

    revealArea(state.player.x, state.player.y, 4, 3500);
    emitProbes("step", { count: 5, speed: 205, life: 0.55, trigger: false, bounce: 1 });

    if (el.overlay) el.overlay.classList.remove("show");
    if (el.levelSelect) el.levelSelect.value = String(state.currentLevel);

    safeText(el.levelStat, String(level.id));
    safeText(el.difficultyStat, level.difficulty);
    safeText(el.missionTitle, `Mission ${level.id}: ${level.name}`);
    safeText(el.missionSubtitle, `${level.difficulty} maze · minimal white probes · monsters use pathfinding.`);
    safeText(el.echoStat, "0+0");
    safeText(el.statusStat, "Playing");
    safeText(el.hintStat, "strong probe wakes monsters");
    updateLevelBest();
  }

  function showOverlay(title, text, buttonText) {
    safeText(el.overlayTitle, title);
    safeText(el.overlayText, text);
    safeText(el.startBtn, buttonText);
    if (el.overlay) el.overlay.classList.add("show");
  }

  function randomJitter(amount) {
    return (Math.random() - 0.5) * amount;
  }

  function emitProbes(kind, options = {}) {
    const count = options.count || 8;
    const speed = options.speed || 260;
    const life = options.life || 0.9;
    const trigger = options.trigger === true;
    const bounce = options.bounce ?? 1;

    for (let i = 0; i < count; i++) {
      const angle = (Math.PI * 2 * i) / count + randomJitter(0.10);
      state.probes.push({
        x: state.player.x,
        y: state.player.y,
        vx: Math.cos(angle) * speed,
        vy: Math.sin(angle) * speed,
        life,
        maxLife: life,
        kind,
        trigger,
        bounceLeft: bounce,
        history: [{ x: state.player.x, y: state.player.y }]
      });
    }

    // Hard cap prevents lag on low-spec computers.
    if (state.probes.length > 55) {
      state.probes.splice(0, state.probes.length - 55);
    }
  }

  function emitManualProbe() {
    const now = performance.now();
    const rapid = now - state.lastManualProbe < 260;
    state.lastManualProbe = now;

    if (rapid) {
      state.stealthCount += 1;
      safeText(el.echoStat, `${state.echoCount}+${state.stealthCount}`);
      safeText(el.hintStat, "soft probe: will not wake monsters");
      emitProbes("soft", {
        count: 7,
        speed: 245,
        life: 0.60,
        trigger: false,
        bounce: 1
      });
      return;
    }

    state.echoCount += 1;
    safeText(el.echoStat, `${state.echoCount}+${state.stealthCount}`);
    safeText(el.hintStat, "strong probe: noisy");
    emitProbes("strong", {
      count: 14,
      speed: 325,
      life: 1.15,
      trigger: true,
      bounce: 3
    });
  }

  function wakeMonster(monster, reason) {
    if (!monster || monster.state === "chase") return;
    monster.state = "chase";
    monster.revealUntil = performance.now() + 9000;
    monster.path = [];
    monster.pathTimer = 0;
    safeText(el.hintStat, reason || "monster chasing");
  }

  function updateProbes(dt) {
    const now = performance.now();

    for (const probe of state.probes) {
      probe.life -= dt;
      if (probe.life <= 0) continue;

      let nx = probe.x + probe.vx * dt;
      let ny = probe.y + probe.vy * dt;

      if (isWallAtPixel(nx, probe.y)) {
        revealTile(nx / TILE, probe.y / TILE, 900);
        if (probe.bounceLeft > 0) {
          probe.vx *= -0.85;
          probe.bounceLeft -= 1;
          nx = probe.x + probe.vx * dt;
        } else {
          probe.life = 0;
          continue;
        }
      }

      if (isWallAtPixel(probe.x, ny)) {
        revealTile(probe.x / TILE, ny / TILE, 900);
        if (probe.bounceLeft > 0) {
          probe.vy *= -0.85;
          probe.bounceLeft -= 1;
          ny = probe.y + probe.vy * dt;
        } else {
          probe.life = 0;
          continue;
        }
      }

      probe.x = Math.max(2, Math.min(WORLD_W - 2, nx));
      probe.y = Math.max(2, Math.min(WORLD_H - 2, ny));

      revealTile(probe.x / TILE, probe.y / TILE, probe.kind === "soft" ? 520 : 900);

      probe.history.push({ x: probe.x, y: probe.y });
      if (probe.history.length > 4) probe.history.shift();

      for (const monster of state.monsters) {
        const d = Math.hypot(monster.x - probe.x, monster.y - probe.y);
        if (d < 46) {
          monster.revealUntil = now + 2400;
          if (probe.trigger && probe.kind === "strong") {
            wakeMonster(monster, "strong probe woke a monster");
          }
        }
      }
    }

    state.probes = state.probes.filter(p => p.life > 0);
  }

  function findPath(startTx, startTy, goalTx, goalTy) {
    if (!isPassable(startTx, startTy) || !isPassable(goalTx, goalTy)) return [];

    const key = (x, y) => `${x},${y}`;
    const queue = [{ x: startTx, y: startTy }];
    const visited = new Set([key(startTx, startTy)]);
    const parent = new Map();
    const dirs = [[1,0], [-1,0], [0,1], [0,-1]];

    while (queue.length > 0) {
      const cur = queue.shift();
      if (cur.x === goalTx && cur.y === goalTy) {
        const path = [];
        let k = key(cur.x, cur.y);
        while (parent.has(k)) {
          const [px, py] = k.split(",").map(Number);
          path.push({ tx: px, ty: py });
          k = parent.get(k);
        }
        path.reverse();
        return path;
      }

      for (const [dx, dy] of dirs) {
        const nx = cur.x + dx;
        const ny = cur.y + dy;
        const nk = key(nx, ny);
        if (visited.has(nk)) continue;
        if (!isPassable(nx, ny)) continue;
        visited.add(nk);
        parent.set(nk, key(cur.x, cur.y));
        queue.push({ x: nx, y: ny });
      }
    }

    return [];
  }

  function updateMonsters(dt) {
    const playerTx = Math.floor(state.player.x / TILE);
    const playerTy = Math.floor(state.player.y / TILE);
    const now = performance.now();

    for (const monster of state.monsters) {
      const distToPlayer = Math.hypot(state.player.x - monster.x, state.player.y - monster.y);

      if (distToPlayer < monster.r + state.player.radius + 3) {
        state.mode = "lost";
        state.deathCount = 1;
        safeText(el.statusStat, "Caught");
        safeText(el.hintStat, "monster caught you");
        submitResult("loss");
        showOverlay(
          "Caught",
          `A monster caught you after ${state.elapsed.toFixed(1)} seconds. Strong probes wake monsters. Rapid probes are safer but dimmer.`,
          "Restart Level"
        );
        return;
      }

      if (monster.state === "sleep" && distToPlayer < 78) {
        wakeMonster(monster, "you walked too close");
      }

      if (monster.state !== "chase") continue;

      monster.revealUntil = now + 1200;
      monster.pathTimer -= dt;

      const mtx = Math.floor(monster.x / TILE);
      const mty = Math.floor(monster.y / TILE);

      if (monster.pathTimer <= 0 || !monster.path || monster.path.length === 0) {
        monster.path = findPath(mtx, mty, playerTx, playerTy);
        monster.pathTimer = 0.22;
      }

      let target = monster.path && monster.path.length > 0 ? monster.path[0] : { tx: playerTx, ty: playerTy };
      const targetX = target.tx * TILE + TILE / 2;
      const targetY = target.ty * TILE + TILE / 2;

      const dx = targetX - monster.x;
      const dy = targetY - monster.y;
      const len = Math.hypot(dx, dy) || 1;

      if (len < 3 && monster.path && monster.path.length > 0) {
        monster.path.shift();
        continue;
      }

      const step = monster.speed * dt;
      const nx = monster.x + (dx / len) * step;
      const ny = monster.y + (dy / len) * step;

      if (canMoveTo(nx, monster.y, monster.r * 0.75)) monster.x = nx;
      if (canMoveTo(monster.x, ny, monster.r * 0.75)) monster.y = ny;
    }
  }

  function checkEndConditions() {
    const tile = tileAtPixel(state.player.x, state.player.y);

    if (tile === "^") {
      state.mode = "lost";
      state.deathCount = 1;
      safeText(el.statusStat, "Dead");
      safeText(el.hintStat, "trap hit");
      submitResult("loss");
      showOverlay(
        "Signal Lost",
        `You touched a trap after ${state.elapsed.toFixed(1)} seconds.`,
        "Restart Level"
      );
    }

    if (tile === "E") {
      state.mode = "won";
      safeText(el.statusStat, "Cleared");
      safeText(el.hintStat, "saved");
      submitResult("win");
      showOverlay(
        "Level Cleared",
        `Finished in ${state.elapsed.toFixed(1)} seconds. Strong probes: ${state.echoCount}. Soft probes: ${state.stealthCount}.`,
        state.currentLevel === LEVELS.length - 1 ? "Replay Level" : "Next Level"
      );
    }
  }

  function handleInput(dt) {
    const p = state.player;
    let ax = 0;
    let ay = 0;

    if (state.keys.has("arrowup") || state.keys.has("w")) ay -= 1;
    if (state.keys.has("arrowdown") || state.keys.has("s")) ay += 1;
    if (state.keys.has("arrowleft") || state.keys.has("a")) ax -= 1;
    if (state.keys.has("arrowright") || state.keys.has("d")) ax += 1;

    if (ax !== 0 || ay !== 0) {
      const len = Math.hypot(ax, ay);
      ax /= len;
      ay /= len;

      p.vx += ax * p.accel * dt;
      p.vy += ay * p.accel * dt;

      const now = performance.now();
      if (now - state.lastStepProbe > 420) {
        emitProbes("step", {
          count: 3,
          speed: 200,
          life: 0.48,
          trigger: false,
          bounce: 1
        });
        state.lastStepProbe = now;
      }
    }

    const speed = Math.hypot(p.vx, p.vy);
    if (speed > p.maxSpeed) {
      p.vx = (p.vx / speed) * p.maxSpeed;
      p.vy = (p.vy / speed) * p.maxSpeed;
    }

    p.vx *= Math.pow(p.friction, dt * 60);
    p.vy *= Math.pow(p.friction, dt * 60);

    const nx = p.x + p.vx * dt;
    const ny = p.y + p.vy * dt;

    if (canMoveTo(nx, p.y, p.radius)) p.x = nx;
    else p.vx *= -0.12;

    if (canMoveTo(p.x, ny, p.radius)) p.y = ny;
    else p.vy *= -0.12;

    revealArea(p.x, p.y, 2, 850);
  }

  function update(dt) {
    if (state.mode !== "playing") return;

    state.elapsed = (performance.now() - state.startAt) / 1000;
    safeText(el.timeStat, state.elapsed.toFixed(1) + "s");

    handleInput(dt);
    updateProbes(dt);
    updateMonsters(dt);
    checkEndConditions();
  }

  function drawBackground() {
    ctx.fillStyle = "#020202";
    ctx.fillRect(0, 0, WORLD_W, WORLD_H);
  }

  function drawTiles() {
    const now = performance.now();

    for (let y = 0; y < ROWS; y++) {
      for (let x = 0; x < COLS; x++) {
        const tile = state.grid[y][x];
        if (tile === ".") continue;

        const visible = Math.max(0, state.reveal[y][x] - now);
        const memory = Math.max(0, state.memory[y][x] - now);

        if (visible <= 0 && memory <= 0) continue;

        const alpha = visible > 0
          ? Math.min(0.9, 0.25 + visible / 1400)
          : Math.min(0.18, memory / 5000 * 0.18);

        const px = x * TILE;
        const py = y * TILE;

        if (tile === "#") {
          ctx.fillStyle = `rgba(220,220,220,${alpha * 0.30})`;
          ctx.fillRect(px + 4, py + 4, TILE - 8, TILE - 8);
          ctx.strokeStyle = `rgba(255,255,255,${alpha * 0.45})`;
          ctx.strokeRect(px + 4, py + 4, TILE - 8, TILE - 8);
        } else if (tile === "^") {
          ctx.fillStyle = `rgba(255,80,100,${alpha * 0.70})`;
          ctx.beginPath();
          ctx.moveTo(px + TILE / 2, py + 7);
          ctx.lineTo(px + TILE - 7, py + TILE - 7);
          ctx.lineTo(px + 7, py + TILE - 7);
          ctx.closePath();
          ctx.fill();
        } else if (tile === "E") {
          ctx.strokeStyle = `rgba(100,255,160,${alpha * 0.85})`;
          ctx.lineWidth = 2;
          ctx.beginPath();
          ctx.arc(px + TILE / 2, py + TILE / 2, 12, 0, Math.PI * 2);
          ctx.stroke();
          ctx.lineWidth = 1;
        }
      }
    }
  }

  function drawProbes() {
    for (const probe of state.probes) {
      const a = Math.max(0, probe.life / probe.maxLife);

      if (probe.kind === "soft") {
        ctx.strokeStyle = `rgba(180,180,180,${0.22 * a})`;
        ctx.fillStyle = `rgba(200,200,200,${0.32 * a})`;
        ctx.lineWidth = 1;
      } else if (probe.kind === "step") {
        ctx.strokeStyle = `rgba(230,230,230,${0.26 * a})`;
        ctx.fillStyle = `rgba(240,240,240,${0.36 * a})`;
        ctx.lineWidth = 1;
      } else {
        ctx.strokeStyle = `rgba(255,255,255,${0.72 * a})`;
        ctx.fillStyle = `rgba(255,255,255,${0.88 * a})`;
        ctx.lineWidth = 1.5;
      }

      ctx.beginPath();
      for (let i = 0; i < probe.history.length; i++) {
        const point = probe.history[i];
        if (i === 0) ctx.moveTo(point.x, point.y);
        else ctx.lineTo(point.x, point.y);
      }
      ctx.stroke();

      ctx.beginPath();
      ctx.arc(probe.x, probe.y, probe.kind === "strong" ? 2.7 : 2.0, 0, Math.PI * 2);
      ctx.fill();
    }
  }

  function drawMonsters() {
    const now = performance.now();

    for (const monster of state.monsters) {
      const visible = monster.state === "chase" || monster.revealUntil > now;
      if (!visible) continue;

      const alpha = monster.state === "chase" ? 1 : Math.max(0.25, (monster.revealUntil - now) / 1800);

      ctx.fillStyle = monster.state === "chase"
        ? `rgba(255,40,70,${alpha})`
        : `rgba(255,100,120,${0.55 * alpha})`;

      ctx.beginPath();
      ctx.arc(monster.x, monster.y, monster.r, 0, Math.PI * 2);
      ctx.fill();

      if (monster.state === "chase") {
        ctx.strokeStyle = "rgba(255,160,170,0.75)";
        ctx.beginPath();
        ctx.arc(monster.x, monster.y, monster.r + 5, 0, Math.PI * 2);
        ctx.stroke();
      }
    }
  }

  function drawPlayer() {
    const p = state.player;

    ctx.fillStyle = "rgba(255,255,255,1)";
    ctx.beginPath();
    ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
    ctx.fill();

    ctx.strokeStyle = "rgba(255,255,255,0.55)";
    ctx.beginPath();
    ctx.arc(p.x, p.y, p.radius + 6, 0, Math.PI * 2);
    ctx.stroke();
  }

  function drawInstructionText() {
    if (state.mode !== "playing" || state.elapsed > 8) return;

    ctx.fillStyle = "rgba(255,255,255,0.80)";
    ctx.font = "700 16px Arial, sans-serif";
    ctx.textAlign = "center";
    ctx.fillText("Strong probe wakes monsters. Rapid E/Space = dim soft probe. Monsters now pathfind and chase.", WORLD_W / 2, 42);
  }

  function draw() {
    ctx.setTransform(state.scale, 0, 0, state.scale, 0, 0);
    ctx.imageSmoothingEnabled = false;

    drawBackground();
    drawTiles();
    drawProbes();
    drawMonsters();
    drawPlayer();
    drawInstructionText();
  }

  let lastTime = performance.now();

  function frame(now) {
    try {
      const dt = Math.min(0.033, (now - lastTime) / 1000);
      lastTime = now;

      state.fpsFrames += 1;
      state.fpsTotal += 1 / Math.max(dt, 0.001);
      state.fpsTime += dt;
      if (state.fpsTime > 0.7) {
        safeText(el.fpsLabel, "FPS: " + Math.round(state.fpsTotal / state.fpsFrames));
        state.fpsFrames = 0;
        state.fpsTotal = 0;
        state.fpsTime = 0;
      }

      update(dt);
      draw();
      requestAnimationFrame(frame);
    } catch (err) {
      showFatalError(err);
    }
  }

  function keyName(event) {
    if (event.key === " ") return "space";
    return event.key.toLowerCase();
  }

  function bindEvents() {
    window.addEventListener("keydown", (event) => {
      const k = keyName(event);
      state.keys.add(k);

      if (["arrowup", "arrowdown", "arrowleft", "arrowright", "space"].includes(k)) {
        event.preventDefault();
      }

      if ((k === "space" || k === "e") && state.mode === "playing") {
        emitManualProbe();
      }

      if (k === "r") loadLevel(state.currentLevel);

      if (k === "p" && state.mode === "playing") {
        state.mode = "paused";
        safeText(el.statusStat, "Paused");
        showOverlay("Paused", "The game is paused. Press Start to restart the selected level.", "Restart Level");
      }
    });

    window.addEventListener("keyup", (event) => state.keys.delete(keyName(event)));
    window.addEventListener("resize", setupCanvas);

    if (el.startBtn) {
      el.startBtn.addEventListener("click", () => {
        if (state.mode === "won" && state.currentLevel < LEVELS.length - 1) {
          loadLevel(state.currentLevel + 1);
        } else {
          loadLevel(state.currentLevel);
        }
      });
    }

    if (el.levelBtn) {
      el.levelBtn.addEventListener("click", () => {
        state.currentLevel = (state.currentLevel + 1) % LEVELS.length;
        if (el.levelSelect) el.levelSelect.value = String(state.currentLevel);
        const level = LEVELS[state.currentLevel];
        safeText(el.levelStat, String(level.id));
        safeText(el.difficultyStat, level.difficulty);
        showOverlay(`Level ${level.id}`, `${level.name} selected. Difficulty: ${level.difficulty}.`, "Start Level " + level.id);
        updateLevelBest();
      });
    }

    if (el.levelSelect) {
      el.levelSelect.addEventListener("change", () => {
        state.currentLevel = Number(el.levelSelect.value) || 0;
        const level = LEVELS[state.currentLevel];
        safeText(el.levelStat, String(level.id));
        safeText(el.difficultyStat, level.difficulty);
        showOverlay(`Level ${level.id}`, `${level.name} selected. Difficulty: ${level.difficulty}.`, "Start Level " + level.id);
        updateLevelBest();
      });
    }
  }

  function initPreview() {
    state.grid = normaliseRows(LEVELS[0].map).map(row => row.split(""));
    state.reveal = Array.from({ length: ROWS }, () => Array(COLS).fill(performance.now() + 1800));
    state.memory = Array.from({ length: ROWS }, () => Array(COLS).fill(performance.now() + 1800));
    state.monsters = [];
    draw();
  }

  function init() {
    getElements();
    populateLevelSelect();
    setupCanvas();
    bindEvents();
    loadSummary();
    initPreview();
    requestAnimationFrame(frame);
  }

  document.addEventListener("DOMContentLoaded", () => {
    try {
      init();
    } catch (err) {
      showFatalError(err);
    }
  });
})();
