import os
import subprocess
import tempfile

# 🚀 每批次最大文件大小（2GB）
MAX_BATCH_SIZE_GB = 2.0
MAX_BATCH_SIZE_BYTES = MAX_BATCH_SIZE_GB * 1024 * 1024 * 1024

# 🚀 远程 Git 分支
BRANCH_NAME = "master"

def get_untracked_files():
    """ 获取未跟踪的文件列表 """
    result = subprocess.run(['git', 'ls-files', '--others', '--exclude-standard'],
                            stdout=subprocess.PIPE, text=True)
    files = result.stdout.strip().split("\n")
    return [f for f in files if f]  # 过滤掉空行

def get_file_size(file_path):
    """ 获取文件大小（字节）"""
    return os.path.getsize(file_path) if os.path.exists(file_path) else 0

def commit_untracked_files():
    """ 按 2GB 批次提交未跟踪的文件，并每次 commit 立即 push """
    print("🔍 正在检查未跟踪的文件...")
    untracked_files = get_untracked_files()

    if not untracked_files:
        print("✅ 没有未跟踪的文件，脚本结束。")
        return

    current_batch = []
    current_size = 0

    for file in untracked_files:
        file_size = get_file_size(file)
        
        # 如果单个文件超过 2GB，跳过（避免 push 失败）
        if file_size > MAX_BATCH_SIZE_BYTES:
            print(f"⚠️ 文件 {file} 超过 2GB，跳过提交。")
            continue

        # 如果加上当前文件后超过 2GB，提交当前批次
        if current_size + file_size > MAX_BATCH_SIZE_BYTES:
            commit_and_push(current_batch)
            current_batch = []
            current_size = 0

        # 添加文件到当前批次
        current_batch.append(file)
        current_size += file_size
        print(f"✅ 文件 {file} 已添加，当前批次总大小: {current_size / (1024**3):.2f} GB")

    # 提交最后一个批次
    if current_batch:
        commit_and_push(current_batch)



def commit_and_push(files):
    """ 提交并推送当前批次的文件 """
    if not files:
        return

    print(f"\n📦 提交 {len(files)} 个文件，总大小不超过 2GB...")

    try:
        # **使用临时文件存储文件路径**
        with tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8') as temp_file:
            temp_file.write('\n'.join(files))
            temp_file_name = temp_file.name  # 获取临时文件路径
        
        # ✅ **使用 `--pathspec-from-file` 避免 Windows 参数长度限制**
        subprocess.run(['git', 'add', '--pathspec-from-file=' + temp_file_name], check=True)

        # 提交更改
        commit_message = f"Auto-commit {len(files)} files"
        subprocess.run(['git', 'commit', '-m', commit_message], check=True)

        # 推送更改
        print("🚀 正在 push 到远程仓库...")
        subprocess.run(['git', 'push', 'origin', BRANCH_NAME], check=True)

        print("✅ 提交并推送成功！\n")

    except subprocess.CalledProcessError as e:
        print(f"❌ Git 操作失败: {e}")




if __name__ == "__main__":
    print("🚀 启动 Git 提交脚本...")
    commit_untracked_files()
    print("🎉 脚本执行完毕！")
