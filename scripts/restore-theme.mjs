#!/usr/bin/env node
import crypto from "node:crypto";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { spawnSync } from "node:child_process";

const args = process.argv.slice(2);
const getArg = (name, fallback = "") => {
  const i = args.indexOf(name);
  return i >= 0 && args[i + 1] ? args[i + 1] : fallback;
};

function defaultTarget() {
  if (process.platform === "darwin") {
    return "/Applications/WorkBuddy.app/Contents/Resources/app.asar";
  }
  if (process.platform === "win32") {
    const candidates = [
      path.join(os.homedir(), "AppData", "Local", "Programs", "WorkBuddy", "resources", "app.asar"),
      path.join(os.homedir(), "AppData", "Local", "Programs", "workbuddy", "resources", "app.asar"),
      "C:\\Program Files\\WorkBuddy\\resources\\app.asar",
      "C:\\Program Files (x86)\\WorkBuddy\\resources\\app.asar",
    ];
    for (const c of candidates) {
      if (fs.existsSync(c)) return c;
    }
    return candidates[0];
  }
  throw new Error(`不支持的平台: ${process.platform}, 请用 --target 手动指定 app.asar 路径`);
}

function checkRunning() {
  if (process.platform === "darwin") {
    const r = spawnSync("/usr/bin/pgrep", ["-fl", "/Applications/WorkBuddy.app/Contents/Frameworks/WorkBuddy Helper"], { encoding: "utf8" });
    return Boolean((r.stdout || "").trim());
  }
  if (process.platform === "win32") {
    const r = spawnSync("tasklist", ["/FI", "IMAGENAME eq WorkBuddy.exe", "/NH"], { encoding: "utf8" });
    return (r.stdout || "").toLowerCase().includes("workbuddy.exe");
  }
  return false;
}

const backup = path.resolve(getArg("--backup"));
const target = path.resolve(getArg("--target", defaultTarget()));
const allowRunning = args.includes("--allow-running");
if (!backup || !fs.existsSync(backup)) throw new Error("请使用 --backup 指定备份 app.asar");
if (!fs.existsSync(target)) throw new Error(`找不到 WorkBuddy 资源：${target}`);

const isRunning = checkRunning();
if (isRunning && !allowRunning) throw new Error("WorkBuddy 仍在运行。请完全退出应用后再恢复，或在测试副本时传入 --allow-running。");

const hash = (file) => crypto.createHash("sha256").update(fs.readFileSync(file)).digest("hex");
const temp = `${target}.skin-restoring`;
fs.copyFileSync(backup, temp);
if (hash(backup) !== hash(temp)) {
  fs.rmSync(temp, { force: true });
  throw new Error("恢复文件校验失败，当前应用未改动。");
}
fs.renameSync(temp, target);
console.log(JSON.stringify({ restored: true, target, backup, sha256: hash(target) }, null, 2));
