#!/bin/bash

# GitFlow 分支状态检查脚本

echo "🎯 CastMind GitFlow 分支状态检查"
echo "================================="
echo ""

# 检查当前分支
current_branch=$(git branch --show-current)
echo "当前分支: $current_branch"
echo ""

# 显示所有分支
echo "📋 分支列表:"
echo "------------"
git branch -a | grep -E "(main|develop|feature/|release/|hotfix/)" | sed 's/^/  /'
echo ""

# 显示远程分支
echo "🌐 远程分支:"
echo "------------"
git branch -r | grep -E "(main|develop|feature/|release/|hotfix/)" | sed 's/^/  /'
echo ""

# 显示最近的提交
echo "📝 最近提交:"
echo "------------"
git log --oneline --graph --all --decorate -10
echo ""

# 检查分支状态
echo "✅ 分支状态检查:"
echo "----------------"

# 检查 main 分支
if git branch -a | grep -q "main"; then
    echo "  ✅ main 分支存在"
else
    echo "  ❌ main 分支不存在"
fi

# 检查 develop 分支
if git branch -a | grep -q "develop"; then
    echo "  ✅ develop 分支存在"
else
    echo "  ❌ develop 分支不存在"
fi

# 检查功能分支
feature_branches=$(git branch -a | grep "feature/" | wc -l)
if [ $feature_branches -gt 0 ]; then
    echo "  ✅ 功能分支: $feature_branches 个"
    git branch -a | grep "feature/" | sed 's/^/    /'
else
    echo "  ℹ️  暂无功能分支"
fi

echo ""
echo "🚀 GitFlow 命令参考:"
echo "-------------------"
echo "  创建功能分支: git checkout -b feature/名称 develop"
echo "  创建发布分支: git checkout -b release/版本号 develop"
echo "  创建热修复分支: git checkout -b hotfix/名称 main"
echo "  合并功能分支: git checkout develop && git merge --no-ff feature/名称"
echo "  推送分支: git push -u origin 分支名"
echo ""

# 显示 GitHub PR 链接
echo "🔗 GitHub Pull Requests:"
echo "------------------------"
echo "  https://github.com/YearsAlso/castmind-app/pulls"
echo ""

echo "🎭 当前个性化功能分支: feature/personalization"
echo "  包含功能: 主题切换、个性化统计、增强API、UI优化"
echo ""