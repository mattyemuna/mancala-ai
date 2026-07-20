(() => {
  "use strict";

  const TOP_ROW_ORDER = [12, 11, 10, 9, 8, 7];
  const BOTTOM_ROW_ORDER = [0, 1, 2, 3, 4, 5];
  const MARBLE_COLORS = ["marble-blue", "marble-clear", "marble-green"];
  const FLY_MS = 260;

  let currentState = null;   // last authoritative state from the server
  let displayPits = null;    // 14-length array mirroring what's on screen right now
  let animating = false;

  const pitEls = {};         // pitIndex -> element (0-5, 7-12)
  const storeEls = { 6: null, 13: null };
  const storeCountEls = { 6: null, 13: null };

  const modeScreen = document.getElementById("mode-screen");
  const gameScreen = document.getElementById("game-screen");
  const turnIndicator = document.getElementById("turn-indicator");
  const modeLabelEl = document.getElementById("mode-label");
  const overlay = document.getElementById("gameover-overlay");
  const overlayTitle = document.getElementById("gameover-title");
  const overlaySub = document.getElementById("gameover-sub");

  const MODE_LABELS = { pvp: "Player vs Player", ab: "vs Alpha-Beta AI", sarsa: "vs SARSA AI" };

  function marbleColorClass(pitIndex, slot) {
    const h = (pitIndex * 7 + slot * 13 + slot * slot * 3) % MARBLE_COLORS.length;
    return MARBLE_COLORS[h];
  }

  // ---------------- DOM construction ----------------

  function buildBoardDOM() {
    const topRow = document.querySelector(".pit-row-top");
    const bottomRow = document.querySelector(".pit-row-bottom");
    topRow.innerHTML = "";
    bottomRow.innerHTML = "";

    for (const idx of TOP_ROW_ORDER) topRow.appendChild(makePitEl(idx));
    for (const idx of BOTTOM_ROW_ORDER) bottomRow.appendChild(makePitEl(idx));

    storeEls[6] = document.getElementById("store-p1-well");
    storeEls[13] = document.getElementById("store-p2-well");
    storeCountEls[6] = document.getElementById("store-p1-count");
    storeCountEls[13] = document.getElementById("store-p2-count");
  }

  function makePitEl(index) {
    const el = document.createElement("div");
    el.className = "pit";
    el.dataset.index = String(index);

    const label = document.createElement("span");
    label.className = "pit-index";
    label.textContent = String(index);
    el.appendChild(label);

    el.addEventListener("click", () => onPitClick(index));
    pitEls[index] = el;
    return el;
  }

  // ---------------- Rendering ----------------

  function renderPitOrStore(index) {
    const isStore = index === 6 || index === 13;
    const el = isStore ? storeEls[index] : pitEls[index];
    const count = displayPits[index];

    // clear existing marbles (keep the index label for pits)
    const keep = isStore ? [] : [el.querySelector(".pit-index")];
    el.innerHTML = "";
    keep.forEach((k) => k && el.appendChild(k));

    const visibleCount = isStore ? Math.min(count, 30) : count;
    for (let i = 0; i < visibleCount; i++) {
      const m = document.createElement("div");
      m.className = "marble " + marbleColorClass(index, i);
      el.appendChild(m);
    }

    if (isStore) storeCountEls[index].textContent = String(count);
  }

  function renderAllHard() {
    for (let i = 0; i < 14; i++) renderPitOrStore(i);
  }

  function setPitsInteractive(interactive) {
    for (let i = 0; i < 14; i++) {
      if (i === 6 || i === 13) continue;
      const el = pitEls[i];
      const legal = interactive && currentState && !currentState.gameOver &&
        currentState.legalMoves.includes(i) &&
        (currentState.mode === "pvp" || currentState.currentPlayer === currentState.humanPlayer);
      el.classList.toggle("legal", !!legal);
    }
  }

  function setThinking(isThinking) {
    turnIndicator.classList.toggle("thinking", isThinking);
  }

  function applyUIState(state) {
    modeLabelEl.textContent = MODE_LABELS[state.mode] || state.mode;

    if (state.gameOver) {
      turnIndicator.innerHTML = `<span class="dot"></span> Game over`;
      setThinking(false);
      setPitsInteractive(false);
      showGameOver(state);
      return;
    }

    const isHumanTurn = state.mode === "pvp" || state.currentPlayer === state.humanPlayer;
    const who = state.currentPlayer === 1 ? "Player 1" : (state.mode === "pvp" ? "Player 2" : "AI");
    turnIndicator.innerHTML = `<span class="dot"></span> ${who}'s turn`;
    setThinking(false);
    setPitsInteractive(isHumanTurn);
  }

  function showGameOver(state) {
    let title, sub;
    if (state.winner === 3) {
      title = "It's a tie!";
      sub = `${state.p1Store} — ${state.p2Store}`;
    } else if (state.winner === state.humanPlayer || state.mode === "pvp") {
      title = state.winner === 1 ? "Player 1 wins!" : "Player 2 wins!";
      sub = `${state.p1Store} — ${state.p2Store}`;
    } else {
      title = "AI wins!";
      sub = `${state.p1Store} — ${state.p2Store}`;
    }
    overlayTitle.textContent = title;
    overlaySub.textContent = sub;
    overlay.classList.remove("hidden");
  }

  // ---------------- Flight animation ----------------

  function centerOf(index) {
    const el = (index === 6 || index === 13) ? storeEls[index] : pitEls[index];
    const r = el.getBoundingClientRect();
    return { x: r.left + r.width / 2, y: r.top + r.height / 2 };
  }

  function flyMarble(fromIndex, toIndex, colorClass) {
    return new Promise((resolve) => {
      const from = centerOf(fromIndex);
      const to = centerOf(toIndex);
      const el = document.createElement("div");
      el.className = "fly-marble " + colorClass;
      el.style.left = "0px";
      el.style.top = "0px";
      el.style.transform = `translate(${from.x - 10}px, ${from.y - 10}px)`;
      document.body.appendChild(el);

      // force layout so the browser registers the start position before animating
      // eslint-disable-next-line no-unused-expressions
      el.getBoundingClientRect();

      requestAnimationFrame(() => {
        el.style.transform = `translate(${to.x - 10}px, ${to.y - 10}px)`;
      });

      let done = false;
      const finish = () => {
        if (done) return;
        done = true;
        el.remove();
        resolve();
      };
      el.addEventListener("transitionend", finish, { once: true });
      setTimeout(finish, FLY_MS + 120); // fallback in case transitionend doesn't fire
    });
  }

  async function animateSow(fromIndex, toIndex) {
    const slot = displayPits[toIndex];
    const colorClass = marbleColorClass(toIndex, slot);
    await flyMarble(fromIndex, toIndex, colorClass);
    displayPits[toIndex] += 1;
    renderPitOrStore(toIndex);
  }

  async function animateCapture(step) {
    const { pitIndex, oppositeIndex, storeIndex, amount } = step;
    await Promise.all([
      flyMarble(pitIndex, storeIndex, marbleColorClass(pitIndex, 0)),
      flyMarble(oppositeIndex, storeIndex, marbleColorClass(oppositeIndex, 0)),
    ]);
    displayPits[pitIndex] = 0;
    displayPits[oppositeIndex] = 0;
    displayPits[storeIndex] += amount;
    renderPitOrStore(pitIndex);
    renderPitOrStore(oppositeIndex);
    renderPitOrStore(storeIndex);
  }

  async function animateSweep(sweepSteps) {
    await Promise.all(sweepSteps.map((s) => flyMarble(s.pitIndex, s.storeIndex, marbleColorClass(s.pitIndex, 0))));
    for (const s of sweepSteps) {
      displayPits[s.pitIndex] = 0;
      displayPits[s.storeIndex] += s.amount;
    }
    for (const s of sweepSteps) renderPitOrStore(s.pitIndex);
    renderPitOrStore(6);
    renderPitOrStore(13);
  }

  async function playSteps(steps, sourcePit) {
    displayPits[sourcePit] = 0;
    renderPitOrStore(sourcePit);

    const sweepSteps = [];
    let lastLanded = sourcePit;

    for (const step of steps) {
      if (step.type === "sow") {
        await animateSow(lastLanded, step.pitIndex);
        lastLanded = step.pitIndex;
      } else if (step.type === "capture") {
        await animateCapture(step);
      } else if (step.type === "sweep") {
        sweepSteps.push(step);
      }
    }

    if (sweepSteps.length) await animateSweep(sweepSteps);
  }

  // ---------------- Game flow ----------------

  async function onPitClick(pitIndex) {
    if (animating) return;
    if (!currentState || currentState.gameOver) return;
    if (!currentState.legalMoves.includes(pitIndex)) return;
    if (currentState.mode !== "pvp" && currentState.currentPlayer !== currentState.humanPlayer) return;

    animating = true;
    setPitsInteractive(false);

    try {
      const res = await fetch("/api/move", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ pit: pitIndex }),
      });
      const data = await res.json();
      if (!res.ok) {
        console.error(data.error);
        return;
      }
      await playSteps(data.steps, data.sourcePit);
      currentState = data.state;
      displayPits = [...currentState.pits];
      renderAllHard();
    } finally {
      animating = false;
      afterMove();
    }
  }

  function afterMove() {
    applyUIState(currentState);
    if (!currentState.gameOver && currentState.mode !== "pvp" && currentState.currentPlayer === currentState.aiPlayer) {
      triggerAiMove();
    }
  }

  async function triggerAiMove() {
    animating = true;
    setPitsInteractive(false);
    setThinking(true);

    try {
      const res = await fetch("/api/ai_move", { method: "POST" });
      const data = await res.json();
      if (!res.ok) {
        console.error(data.error);
        return;
      }
      await playSteps(data.steps, data.sourcePit);
      currentState = data.state;
      displayPits = [...currentState.pits];
      renderAllHard();
    } finally {
      animating = false;
      setThinking(false);
      afterMove();
    }
  }

  async function startNewGame(mode) {
    const res = await fetch("/api/new_game", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ mode }),
    });
    const state = await res.json();
    currentState = state;
    displayPits = [...state.pits];

    overlay.classList.add("hidden");
    modeScreen.classList.add("hidden");
    gameScreen.classList.remove("hidden");

    renderAllHard();
    applyUIState(state);
  }

  function backToModeSelect() {
    overlay.classList.add("hidden");
    gameScreen.classList.add("hidden");
    modeScreen.classList.remove("hidden");
  }

  // ---------------- Wiring ----------------

  document.querySelectorAll(".mode-btn").forEach((btn) => {
    btn.addEventListener("click", () => startNewGame(btn.dataset.mode));
  });

  document.getElementById("new-game-btn").addEventListener("click", backToModeSelect);
  document.getElementById("change-mode-btn").addEventListener("click", backToModeSelect);
  document.getElementById("rematch-btn").addEventListener("click", () => {
    if (currentState) startNewGame(currentState.mode);
  });

  buildBoardDOM();
})();
