/**
 * RozeDatePicker — پکیج تقویم تعاملی شمسی و میلادی اختصاصی استودیو رز تکست (@rozetext.ir)
 * پشتیبانی کامل از تقویم جلالی (شمسی) با موتور استاندارد Intl.DateTimeFormat('fa-IR-u-ca-persian')
 * + نمایش تعداد ریلزهای زمان‌بندی‌شده روی هر روز تقویم + انتخاب سریع روزهای پیک (پنج‌شنبه و جمعه)
 */
(function () {
  const FA_WEEKDAYS_SHORT = ["ش", "ی", "د", "س", "چ", "پ🔥", "ج🔥"];
  const FA_WEEKDAYS_FULL = ["یکشنبه", "دوشنبه", "سه‌شنبه", "چهارشنبه", "پنج‌شنبه 🔥", "جمعه 🔥", "شنبه"];

  // Convert JS Date to YYYY-MM-DD local string
  function toIsoDate(dt) {
    const y = dt.getFullYear();
    const m = String(dt.getMonth() + 1).padStart(2, "0");
    const d = String(dt.getDate()).padStart(2, "0");
    return `${y}-${m}-${d}`;
  }

  function parseIsoDate(isoStr) {
    if (!isoStr || !/^\d{4}-\d{2}-\d{2}$/.test(isoStr)) {
      const now = new Date();
      return new Date(now.getFullYear(), now.getMonth(), now.getDate(), 12, 0, 0);
    }
    const [y, m, d] = isoStr.split("-").map(Number);
    return new Date(y, m - 1, d, 12, 0, 0);
  }

  // Extract Persian (Jalali) year, month name, month number, and day using built-in Intl API
  const persianPartsFmt = new Intl.DateTimeFormat("fa-IR-u-ca-persian", {
    year: "numeric",
    month: "long",
    day: "numeric",
  });
  const persianNumericFmt = new Intl.DateTimeFormat("en-US-u-ca-persian", {
    year: "numeric",
    month: "numeric",
    day: "numeric",
  });

  function getJalaliInfo(dt) {
    const parts = persianPartsFmt.formatToParts(dt);
    const numParts = persianNumericFmt.formatToParts(dt);
    let yearFa = "", monthNameFa = "", dayFa = "";
    let jYear = 1405, jMonth = 7, jDay = 6;

    parts.forEach((p) => {
      if (p.type === "year") yearFa = p.value;
      if (p.type === "month") monthNameFa = p.value;
      if (p.type === "day") dayFa = p.value;
    });
    numParts.forEach((p) => {
      if (p.type === "year") jYear = parseInt(p.value, 10);
      if (p.type === "month") jMonth = parseInt(p.value, 10);
      if (p.type === "day") jDay = parseInt(p.value, 10);
    });

    const weekdayFa = FA_WEEKDAYS_FULL[dt.getDay()];
    return {
      jYear,
      jMonth,
      jDay,
      yearFa,
      monthNameFa,
      dayFa,
      weekdayFa,
      fullLabel: `${weekdayFa}، ${dayFa} ${monthNameFa} ${yearFa}`,
      shortLabel: `${dayFa} ${monthNameFa} ${yearFa}`,
      iso: toIsoDate(dt),
    };
  }

  // Inject CSS for the interactive calendar modal/popover
  function injectStyles() {
    if (document.getElementById("roze-datepicker-styles")) return;
    const style = document.createElement("style");
    style.id = "roze-datepicker-styles";
    style.textContent = `
      .roze-dp-wrapper {
        position: relative;
        display: inline-flex;
        align-items: center;
      }
      .roze-dp-trigger {
        display: inline-flex;
        align-items: center;
        justify-content: space-between;
        gap: 10px;
        background: linear-gradient(135deg, rgba(244, 63, 94, 0.14), rgba(99, 102, 241, 0.12));
        border: 1px solid rgba(244, 63, 94, 0.45);
        color: #f8fafc;
        padding: 9px 14px;
        border-radius: 10px;
        font-family: 'Vazirmatn', sans-serif;
        font-size: 13.5px;
        font-weight: 800;
        cursor: pointer;
        transition: all 0.2s ease;
        min-width: 245px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.25);
      }
      .roze-dp-trigger:hover {
        border-color: #fb7185;
        background: linear-gradient(135deg, rgba(244, 63, 94, 0.24), rgba(99, 102, 241, 0.2));
        transform: translateY(-1px);
      }
      .roze-dp-trigger-iso {
        font-size: 11.5px;
        font-weight: 600;
        color: #fda4af;
        background: rgba(0, 0, 0, 0.35);
        padding: 2px 7px;
        border-radius: 6px;
        direction: ltr;
      }
      .roze-dp-popover {
        position: fixed;
        z-index: 99999;
        width: 350px;
        background: #12141f;
        border: 1px solid rgba(244, 63, 94, 0.5);
        border-radius: 16px;
        box-shadow: 0 22px 50px rgba(0, 0, 0, 0.85), 0 0 25px rgba(244, 63, 94, 0.2);
        padding: 16px;
        font-family: 'Vazirmatn', sans-serif;
        color: #f8fafc;
        direction: rtl;
        display: none;
        animation: rozeDpFadeIn 0.16s ease-out;
      }
      @keyframes rozeDpFadeIn {
        from { opacity: 0; transform: translateY(6px) scale(0.98); }
        to { opacity: 1; transform: translateY(0) scale(1); }
      }
      .roze-dp-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 12px;
        background: rgba(255, 255, 255, 0.04);
        padding: 8px 10px;
        border-radius: 10px;
      }
      .roze-dp-nav-btn {
        background: rgba(244, 63, 94, 0.15);
        border: 1px solid rgba(244, 63, 94, 0.35);
        color: #fda4af;
        border-radius: 8px;
        padding: 4px 10px;
        font-family: 'Vazirmatn', sans-serif;
        font-size: 12px;
        font-weight: 800;
        cursor: pointer;
      }
      .roze-dp-nav-btn:hover {
        background: #f43f5e;
        color: #fff;
      }
      .roze-dp-month-title {
        font-size: 15px;
        font-weight: 900;
        color: #fff;
        text-align: center;
      }
      .roze-dp-month-sub {
        font-size: 11px;
        color: #94a3b8;
        display: block;
      }
      .roze-dp-shortcuts {
        display: flex;
        gap: 6px;
        flex-wrap: wrap;
        margin-bottom: 12px;
      }
      .roze-dp-chip {
        flex: 1;
        text-align: center;
        background: rgba(99, 102, 241, 0.12);
        border: 1px solid rgba(99, 102, 241, 0.3);
        color: #c7d2fe;
        border-radius: 8px;
        padding: 5px 6px;
        font-size: 11.5px;
        font-weight: 700;
        cursor: pointer;
        white-space: nowrap;
      }
      .roze-dp-chip:hover {
        background: #6366f1;
        color: #fff;
      }
      .roze-dp-chip.peak {
        background: rgba(244, 63, 94, 0.14);
        border-color: rgba(244, 63, 94, 0.4);
        color: #fda4af;
      }
      .roze-dp-chip.peak:hover {
        background: #f43f5e;
        color: #fff;
      }
      .roze-dp-weekdays {
        display: grid;
        grid-template-columns: repeat(7, 1fr);
        text-align: center;
        font-size: 11.5px;
        font-weight: 800;
        color: #94a3b8;
        margin-bottom: 6px;
      }
      .roze-dp-grid {
        display: grid;
        grid-template-columns: repeat(7, 1fr);
        gap: 5px;
      }
      .roze-dp-day {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.07);
        border-radius: 9px;
        padding: 6px 2px;
        text-align: center;
        cursor: pointer;
        transition: all 0.15s;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        min-height: 46px;
        position: relative;
      }
      .roze-dp-day:hover {
        border-color: #fb7185;
        background: rgba(244, 63, 94, 0.2);
      }
      .roze-dp-day.is-peak-day {
        border-color: rgba(244, 63, 94, 0.28);
        background: rgba(244, 63, 94, 0.06);
      }
      .roze-dp-day.is-selected {
        background: linear-gradient(135deg, #f43f5e, #e11d48) !important;
        border-color: #fda4af !important;
        color: #fff !important;
        box-shadow: 0 4px 12px rgba(244, 63, 94, 0.45);
      }
      .roze-dp-day.is-muted {
        opacity: 0.32;
      }
      .roze-dp-jday {
        font-size: 14px;
        font-weight: 900;
        line-height: 1.1;
      }
      .roze-dp-gday {
        font-size: 9.5px;
        color: #94a3b8;
        direction: ltr;
        margin-top: 2px;
      }
      .roze-dp-day.is-selected .roze-dp-gday {
        color: #ffe4e6;
      }
      .roze-dp-count-dot {
        font-size: 9px;
        font-weight: 800;
        padding: 1px 4px;
        border-radius: 4px;
        margin-top: 2px;
        background: rgba(16, 185, 129, 0.22);
        color: #34d399;
      }
    `;
    document.head.appendChild(style);
  }

  let activeInput = null;
  let viewCenterDate = new Date();
  viewCenterDate.setHours(12, 0, 0, 0);
  let popoverEl = null;

  function ensurePopover() {
    if (popoverEl) return popoverEl;
    injectStyles();
    popoverEl = document.createElement("div");
    popoverEl.className = "roze-dp-popover";
    document.body.appendChild(popoverEl);

    document.addEventListener("mousedown", (e) => {
      if (
        popoverEl.style.display === "block" &&
        !popoverEl.contains(e.target) &&
        !e.target.closest(".roze-dp-trigger")
      ) {
        popoverEl.style.display = "none";
      }
    });
    return popoverEl;
  }

  // Find the start of the Jalali month containing `centerDate`
  function getJalaliMonthStart(centerDate) {
    const info = getJalaliInfo(centerDate);
    const start = new Date(centerDate);
    start.setDate(start.getDate() - (info.jDay - 1));
    return start;
  }

  function countScheduledForDate(isoDate) {
    if (window.APP_STATE && Array.isArray(window.APP_STATE.scripts)) {
      return window.APP_STATE.scripts.filter((s) => s.scheduled_date === isoDate).length;
    }
    return 0;
  }

  function renderPopover() {
    const pop = ensurePopover();
    const monthStart = getJalaliMonthStart(viewCenterDate);
    const mInfo = getJalaliInfo(monthStart);
    const selectedIso = activeInput ? activeInput.value : toIsoDate(viewCenterDate);

    // Build 35 or 42 day cells starting from Saturday of the first week of the Jalali month
    // JS getDay(): 0=Sun..6=Sat -> Persian week offset (Sat=0, Sun=1, ..., Fri=6)
    const firstDayOffset = (monthStart.getDay() + 1) % 7;
    const gridStart = new Date(monthStart);
    gridStart.setDate(gridStart.getDate() - firstDayOffset);

    let cellsHtml = "";
    for (let i = 0; i < 35; i++) {
      const cellDate = new Date(gridStart);
      cellDate.setDate(gridStart.getDate() + i);
      const cInfo = getJalaliInfo(cellDate);
      const isSameMonth = cInfo.jMonth === mInfo.jMonth;
      const isSelected = cInfo.iso === selectedIso;
      const persianCol = (cellDate.getDay() + 1) % 7; // 5 = Thursday, 6 = Friday
      const isPeak = persianCol === 5 || persianCol === 6;
      const scheduledCount = countScheduledForDate(cInfo.iso);

      const cls = [
        "roze-dp-day",
        !isSameMonth ? "is-muted" : "",
        isPeak ? "is-peak-day" : "",
        isSelected ? "is-selected" : "",
      ]
        .filter(Boolean)
        .join(" ");

      cellsHtml += `
        <div class="${cls}" data-iso="${cInfo.iso}" title="${cInfo.fullLabel} (${cInfo.iso})">
          <span class="roze-dp-jday">${cInfo.dayFa}</span>
          <span class="roze-dp-gday">${cellDate.toLocaleDateString("en-US", { month: "short", day: "numeric" })}</span>
          ${scheduledCount > 0 ? `<span class="roze-dp-count-dot">${scheduledCount}/6</span>` : ""}
        </div>
      `;
    }

    const now = new Date();
    const todayIso = toIsoDate(now);
    const todayJalali = getJalaliInfo(now);

    const tmrw = new Date(now);
    tmrw.setDate(tmrw.getDate() + 1);
    const tmrwIso = toIsoDate(tmrw);
    const tmrwJalali = getJalaliInfo(tmrw);

    const dayOfWeek = now.getDay();
    const diffToThu = (4 - dayOfWeek + 7) % 7;
    const thuDate = new Date(now);
    thuDate.setDate(thuDate.getDate() + (diffToThu === 0 && dayOfWeek !== 4 ? 7 : diffToThu));
    const thuIso = toIsoDate(thuDate);
    const thuJalali = getJalaliInfo(thuDate);

    const diffToFri = (5 - dayOfWeek + 7) % 7;
    const friDate = new Date(now);
    friDate.setDate(friDate.getDate() + (diffToFri === 0 && dayOfWeek !== 5 ? 7 : diffToFri));
    const friIso = toIsoDate(friDate);
    const friJalali = getJalaliInfo(friDate);

    pop.innerHTML = `
      <div class="roze-dp-header">
        <button type="button" class="roze-dp-nav-btn" id="rozeDpPrevMonth">❮ ماه قبل</button>
        <div>
          <div class="roze-dp-month-title">📅 ${mInfo.monthNameFa} ${mInfo.yearFa}</div>
          <span class="roze-dp-month-sub">تقویم شمسی و میلادی رز تکست</span>
        </div>
        <button type="button" class="roze-dp-nav-btn" id="rozeDpNextMonth">ماه بعد ❯</button>
      </div>

      <div class="roze-dp-shortcuts">
        <button type="button" class="roze-dp-chip" data-shortcut="${todayIso}">امروز (${todayJalali.jDay} ${todayJalali.monthNameFa})</button>
        <button type="button" class="roze-dp-chip" data-shortcut="${tmrwIso}">فردا (${tmrwJalali.jDay} ${tmrwJalali.monthNameFa})</button>
        <button type="button" class="roze-dp-chip peak" data-shortcut="${thuIso}">پنج‌شنبه 🔥 (${thuJalali.jDay} ${thuJalali.monthNameFa})</button>
        <button type="button" class="roze-dp-chip peak" data-shortcut="${friIso}">جمعه 🔥 (${friJalali.jDay} ${friJalali.monthNameFa})</button>
      </div>

      <div class="roze-dp-weekdays">
        ${FA_WEEKDAYS_SHORT.map((w) => `<span>${w}</span>`).join("")}
      </div>

      <div class="roze-dp-grid">
        ${cellsHtml}
      </div>
    `;

    pop.querySelector("#rozeDpPrevMonth").onclick = (e) => {
      e.stopPropagation();
      const prev = getJalaliMonthStart(viewCenterDate);
      prev.setDate(prev.getDate() - 5);
      viewCenterDate = prev;
      renderPopover();
    };

    pop.querySelector("#rozeDpNextMonth").onclick = (e) => {
      e.stopPropagation();
      const next = getJalaliMonthStart(viewCenterDate);
      next.setDate(next.getDate() + 33);
      viewCenterDate = next;
      renderPopover();
    };

    pop.querySelectorAll("[data-shortcut]").forEach((btn) => {
      btn.onclick = (e) => {
        e.stopPropagation();
        selectIsoDate(btn.getAttribute("data-shortcut"));
      };
    });

    pop.querySelectorAll(".roze-dp-day").forEach((cell) => {
      cell.onclick = (e) => {
        e.stopPropagation();
        selectIsoDate(cell.getAttribute("data-iso"));
      };
    });
  }

  function selectIsoDate(isoStr) {
    if (!activeInput) return;
    activeInput.value = isoStr;
    updateTriggerLabel(activeInput);
    if (popoverEl) popoverEl.style.display = "none";

    // Trigger standard 'change' event so publisher.html / index.html handlers fire immediately
    const evt = new Event("change", { bubbles: true });
    activeInput.dispatchEvent(evt);
  }

  function updateTriggerLabel(inputEl) {
    const triggerBtn = inputEl._rozeTriggerBtn;
    if (!triggerBtn) return;
    const dt = parseIsoDate(inputEl.value);
    const jInfo = getJalaliInfo(dt);
    triggerBtn.innerHTML = `
      <span>🗓️ ${jInfo.fullLabel}</span>
      <span class="roze-dp-trigger-iso">${jInfo.iso}</span>
    `;
  }

  function enhanceDateInput(inputEl) {
    if (!inputEl || inputEl._rozeEnhanced) {
      if (inputEl && inputEl._rozeEnhanced) updateTriggerLabel(inputEl);
      return;
    }
    inputEl._rozeEnhanced = true;

    const wrapper = document.createElement("div");
    wrapper.className = "roze-dp-wrapper";
    inputEl.parentNode.insertBefore(wrapper, inputEl);
    wrapper.appendChild(inputEl);

    // Hide raw browser date input visually while keeping it in DOM for value/events
    inputEl.style.position = "absolute";
    inputEl.style.opacity = "0";
    inputEl.style.pointerEvents = "none";
    inputEl.style.width = "1px";
    inputEl.style.height = "1px";

    const triggerBtn = document.createElement("button");
    triggerBtn.type = "button";
    triggerBtn.className = "roze-dp-trigger";
    inputEl._rozeTriggerBtn = triggerBtn;
    wrapper.appendChild(triggerBtn);

    updateTriggerLabel(inputEl);

    triggerBtn.addEventListener("click", (e) => {
      e.stopPropagation();
      activeInput = inputEl;
      viewCenterDate = parseIsoDate(inputEl.value);
      renderPopover();
      const rect = triggerBtn.getBoundingClientRect();
      const pop = ensurePopover();
      pop.style.display = "block";

      let top = rect.bottom + 8;
      let left = rect.left;
      if (top + 360 > window.innerHeight) {
        top = Math.max(12, rect.top - 365);
      }
      if (left + 355 > window.innerWidth) {
        left = Math.max(12, window.innerWidth - 365);
      }
      pop.style.top = `${top}px`;
      pop.style.left = `${left}px`;
    });
  }

  function enhanceAllDateInputs() {
    injectStyles();
    document.querySelectorAll('input[type="date"]').forEach(enhanceDateInput);
  }

  window.RozeDatePicker = {
    enhanceAll: enhanceAllDateInputs,
    enhance: enhanceDateInput,
    getJalaliInfo: (isoStr) => getJalaliInfo(parseIsoDate(isoStr)),
  };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", enhanceAllDateInputs);
  } else {
    enhanceAllDateInputs();
  }
})();
