#!/usr/bin/env node
/**
 * Cross-platform, confirmation-first wrapper around Vercel Skills CLI.
 * It does not hard-code an Agent or Skill installation directory.
 */
import readline from "node:readline";
import { spawn } from "node:child_process";

const isWindows = process.platform === "win32";
const npx = isWindows ? "npx.cmd" : "npx";

function run(command, args) {
  return new Promise((resolve) => {
    const child = spawn(command, args, {
      stdio: "inherit",
      shell: isWindows,
      env: process.env,
    });
    child.on("error", (err) => {
      console.error(`无法启动 ${command}：${err.message}`);
      resolve(127);
    });
    child.on("close", (code) => resolve(code ?? 1));
  });
}

function ask(question) {
  const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout,
  });
  return new Promise((resolve) => {
    rl.question(question, (answer) => {
      rl.close();
      resolve(answer.trim().toLowerCase());
    });
  });
}

const checkCode = await run(npx, ["skills", "check"]);
if (checkCode !== 0) {
  console.error("\n更新检查命令未正常完成。为避免误操作，本次不会执行更新。");
  process.exit(checkCode);
}

console.log("\n请先阅读上方检查结果。");
const answer = await ask("是否继续运行更新命令？只有输入 y 才会继续 [y/N] ");
if (answer !== "y" && answer !== "yes") {
  console.log("已取消；没有执行更新命令。");
  process.exit(0);
}

const updateCode = await run(npx, ["skills", "update"]);
if (updateCode !== 0) {
  console.error("\n更新命令未正常完成。请检查上方 CLI 输出。");
  process.exit(updateCode);
}
console.log("\n更新命令已结束。请检查 CLI 输出确认各 Skill 的结果。");
