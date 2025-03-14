import os
import datetime
from io import BytesIO
from PIL import Image
from dotenv import load_dotenv
from google import genai
from google.genai import types


def init_session():
    """
    Initialize the session: load environment variables, create folders, and generate the Markdown file path.
    初始化会话：加载环境变量、创建文件夹、生成 Markdown 文件路径
    """
    load_dotenv()
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        # Raise an error if the API key is missing / 若 API 密钥缺失则抛出错误，在 .env 文件中设置
        raise ValueError("GEMINI_API_KEY is missing. Please set it in the .env file.")

    # Initialize client / 初始化客户端
    client = genai.Client(api_key=api_key)

    # Generate folder name by timestamp / 使用时间戳生成文件夹名称
    timestamp = datetime.datetime.now().strftime("%Y.%m.%d_%H:%M:%S")
    session_title = f"chat_{timestamp}"
    main_folder = os.path.join("output", session_title)
    os.makedirs(main_folder, exist_ok=True)

    # Create image folder / 创建图片文件夹
    image_folder = os.path.join(main_folder, "images")
    os.makedirs(image_folder, exist_ok=True)

    # Markdown file path / Markdown 文件路径
    md_file_path = os.path.join(main_folder, "index.md")

    return {
        "client": client,
        "main_folder": main_folder,
        "image_folder": image_folder,
        "md_file_path": md_file_path,
        "session_title": session_title
    }


def append_to_markdown(md_file_path, content):
    """
    Append content to the Markdown file.
    将内容追加写入 Markdown 文件
    """
    with open(md_file_path, "a", encoding="utf-8") as f:
        f.write(content)


def process_api_response(response, message_count, image_folder):
    """
    Process the API response: print text to console, save images locally, and generate Markdown-format text.
    处理 API 返回结果，将文本输出到终端，并保存图片到本地，同时生成 Markdown 格式文本
    """
    md_snippet = ""

    # Boundary check: if no candidates, return empty string immediately
    # 边界检查：若无候选项，直接返回空字符串
    if not response or not response.candidates:
        return md_snippet

    # Only handle the first candidate for simplicity / 仅处理第一个候选结果
    parts = response.candidates[0].content.parts
    if not parts:
        return md_snippet

    # Traverse each part in the candidate / 遍历候选结果中的各个部分
    for i, part in enumerate(parts):
        if part.text is not None:
            print("GeminiBot:", part.text)
            md_snippet += part.text + "\n\n"
        elif part.inline_data is not None:
            image_filename = f"message{message_count}_image_{i + 1}.png"
            image_path = os.path.join(image_folder, image_filename)
            image_rel_path = os.path.join("images", image_filename)
            try:
                # Save image / 保存图片
                image = Image.open(BytesIO(part.inline_data.data))
                image.save(image_path)
                print(f"Image saved to: {image_path}")
                # Insert an image link into Markdown / 在 Markdown 中插入图片链接
                md_snippet += f"![Generated Image {i + 1}]({image_rel_path})\n\n"
            except Exception as e:
                error_msg = f"Error saving image: {e}"
                print(error_msg)
                md_snippet += error_msg + "\n\n"

    return md_snippet


def main():
    """
    Main function: initialize the session, loop for user input, and generate responses.
    主函数：初始化会话、循环获取用户输入并生成回复
    """
    # Initialize session / 初始化会话
    session = init_session()
    client = session["client"]
    md_file_path = session["md_file_path"]
    image_folder = session["image_folder"]

    # Write initial information to Markdown / 将初始信息写入 Markdown
    init_md = f"# Chat Session: {session['session_title']}\n\n"
    init_md += f"**Start Time:** {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
    with open(md_file_path, "w", encoding="utf-8") as f:
        f.write(init_md)

    # Start the conversation / 开始对话，输入 'exit' 或 'quit' 结束对话
    print("Welcome to the conversation tool. Type 'exit' or 'quit' to end the conversation.")
    message_count = 1

    while True:
        try:
            user_input = input("User: ").strip()
        except KeyboardInterrupt:
            # Gracefully handle Ctrl + C / 优雅地处理 Ctrl + C
            print("\nConversation ended by user.")
            break

        if user_input.lower() in ["exit", "quit"]:
            print("Conversation ended.")
            break

        if not user_input:
            # Skip empty input / 跳过空输入
            continue

        # Get timestamp for each message / 为每条消息记录时间戳
        message_timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Append user input to Markdown / 将用户输入追加写入 Markdown
        user_md = f"**User [{message_timestamp}]:** {user_input}\n\n"
        append_to_markdown(md_file_path, user_md)

        # Call the API to generate a response / 调用 API 生成回复
        try:
            response = client.models.generate_content(
                model="models/gemini-2.0-flash-exp",
                contents=user_input,
                config=types.GenerateContentConfig(response_modalities=['Text', 'Image'])
            )
        except Exception as e:
            error_msg = f"Error calling API: {e}"
            print(error_msg)
            append_to_markdown(md_file_path, error_msg + "\n\n")
            continue

        # Process the response and generate Markdown content / 处理回复，生成 Markdown 内容
        bot_md_header = f"**GeminiBot [{message_timestamp}]:**\n\n"
        bot_md_body = process_api_response(response, message_count, image_folder)

        # Append bot response to Markdown / 将 Bot 的回复追加写入 Markdown
        append_to_markdown(md_file_path, bot_md_header + bot_md_body)

        message_count += 1

    # Print the path to the saved Markdown file / 打印对话保存的 Markdown 路径
    print(f"\nAll conversation content has been saved in: {session['main_folder']}")


if __name__ == "__main__":
    main()
