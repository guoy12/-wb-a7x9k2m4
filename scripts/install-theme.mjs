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

// ---------- 跨平台: 默认 target 路径 ----------
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
    return candidates[0]; // 都不存在时返回第一个, 让下面的 existsSync 报错提示
  }
  throw new Error(`不支持的平台: ${process.platform}, 请用 --target 手动指定 app.asar 路径`);
}

// ---------- 跨平台: 检查 WorkBuddy 是否在运行 ----------
function checkRunning() {
  if (process.platform === "darwin") {
    const r = spawnSync("/usr/bin/pgrep", ["-fl", "/Applications/WorkBuddy.app/Contents/Frameworks/WorkBuddy Helper"], { encoding: "utf8" });
    return Boolean((r.stdout || "").trim());
  }
  if (process.platform === "win32") {
    const r = spawnSync("tasklist", ["/FI", "IMAGENAME eq WorkBuddy.exe", "/NH"], { encoding: "utf8" });
    const out = (r.stdout || "").toLowerCase();
    return out.includes("workbuddy.exe");
  }
  return false;
}

const patched = path.resolve(getArg("--patched"));
// --target 为空字符串时也 fallback 到默认路径
const targetArg = getArg("--target");
const target = path.resolve(targetArg || defaultTarget());
const backupRoot = path.resolve(getArg("--backup-dir", path.join(os.homedir(), ".workbuddy", "backups", "workbuddy-skin")));
const allowRunning = args.includes("--allow-running");

if (!patched || !fs.existsSync(patched)) throw new Error("请使用 --patched 指定已验证的补丁 asar");
if (!fs.existsSync(target)) throw new Error(`找不到 WorkBuddy 资源：${target}\n请用 --target 指定 app.asar 完整路径，例如: --target "D:\\WorkBuddy\\resources\\app.asar"`);

const isRunning = checkRunning();
if (isRunning && !allowRunning) throw new Error("WorkBuddy 仍在运行。请完全退出应用后再安装（系统托盘右键退出），或在明确承担风险后传入 --allow-running。");
if (isRunning && allowRunning) console.warn("WorkBuddy 正在运行：将原子替换资源文件，必须完全退出并重启后才会生效。");

const hash = (file) => crypto.createHash("sha256").update(fs.readFileSync(file)).digest("hex");
const stamp = new Date().toISOString().replaceAll(":", "-");
const backupDir = path.join(backupRoot, stamp);
const backup = path.join(backupDir, "app.asar");
const temp = `${target}.skin-installing`;
fs.mkdirSync(backupDir, { recursive: true });
fs.copyFileSync(target, backup);
if (hash(target) !== hash(backup)) throw new Error("备份校验失败，已停止安装。");

fs.copyFileSync(patched, temp);
if (hash(patched) !== hash(temp)) {
  fs.rmSync(temp, { force: true });
  throw new Error("补丁复制校验失败，原应用未改动。");
}
fs.renameSync(temp, target);

const receipt = {
  installedAt: new Date().toISOString(),
  target,
  backup,
  originalSha256: hash(backup),
  patchedSha256: hash(target)
};
fs.writeFileSync(path.join(backupDir, "receipt.json"), `${JSON.stringify(receipt, null, 2)}\n`);
console.log(JSON.stringify(receipt, null, 2));
