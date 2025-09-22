import pickle
import random
import re
import tkinter as tk
from tkinter import scrolledtext, messagebox
from typing import List, Dict, Tuple, Any, Set
from collections import defaultdict
import json

class StrictRuleBasedProcessor:
    def __init__(self, char_table_path: str):
        # 加载二进制字表文件
        self.char_table = self.load_binary_char_table(char_table_path)
        
        # 加载所有规则文件
        self.load_all_rules()
        
        # 初始化数据结构
        self.initialize_data_structures()
        
        print("严格规则版系统初始化完成")

    def load_all_rules(self):
        """加载所有规则文件（简化为代码内定义，实际应该从文件读取）"""
        # 汉语完整词性分类
        self.pos_classification = {
            "名": {"全称": "名词", "类别": "实词", "特点": "人、事、物、地点、抽象概念", "示例": "桌子、中国、思想、孔子"},
            "动": {"全称": "动词", "类别": "实词", "特点": "动作、行为、存在、变化", "示例": "跑、看、有、成为"},
            "形": {"全称": "形容词", "类别": "实词", "特点": "性质、状态", "示例": "美丽、高、迅速"},
            "副": {"全称": "副词", "类别": "实词", "特点": "修饰动/形，表示程度、时间、范围", "示例": "很、马上、都"},
            "助": {"全称": "助词", "类别": "虚词", "特点": "结构/动态/语气", "示例": "的、地、得、着、了、过、啊、吗"},
            "叹": {"全称": "叹词", "类别": "虚词", "特点": "感叹、应答", "示例": "唉、啊、哦"},
            "语气": {"全称": "语气词", "类别": "虚词", "特点": "表示语气", "示例": "吧、呀、啦"},
            "时间": {"全称": "时间词", "类别": "特殊", "特点": "时间", "示例": "今天、星期一、刚才"},
        }
        
        # 汉语语句内部结构表
        self.structure_patterns = {
            "定中结构": "区别⁺|时间⁺|处所⁺|形⁺|名⁺|数量⁺|定中⁺ + 名",
            "动宾结构": "动 + 名⁺", 
            "并列结构": "X⁺（X=名|动|形|代|拟）",
            "补充结构": "动 + 形⁺|动⁺ + 助",
            "主谓结构": "名⁺ + 动⁺|形⁺ + 助",
            "助词结构": "实⁺ + 助"
        }
        
        # 功能块 ↔ 词性 ↔ 结构统一表
        self.function_block_rules = {
            "话题": {"允许词性序列": "时间｜处所｜名 + 可选名｜区别｜形", "允许结构": "定中结构"},
            "评述": {"允许词性序列": "名+形｜副+形｜名+动｜副+动", "允许结构": "主谓｜状中｜补充"},
            "感叹": {"允许词性序列": "叹｜语气｜助", "允许结构": "叹词语气式｜助词结构"}
        }

    def initialize_data_structures(self):
        """初始化数据结构"""
        self.echo_words = ["是啊", "确实", "对的", "没错", "嗯"]

    def load_binary_char_table(self, char_table_path: str) -> Dict[str, Dict]:
        """加载二进制字表文件"""
        try:
            with open(char_table_path, 'rb') as f:
                char_data = pickle.load(f)
            
            converted_table = {}
            
            if 'data' in char_data:
                for item in char_data['data']:
                    if '字' in item:
                        char = item['字']
                        converted_table[char] = self.convert_char_format(item)
            else:
                for char, info in char_data.items():
                    if isinstance(info, dict):
                        converted_table[char] = self.convert_char_format(info)
            
            print(f"成功加载字表，包含 {len(converted_table)} 个字符")
            return converted_table
            
        except Exception as e:
            print(f"加载字表失败: {e}，使用测试字表")
            return self.create_detailed_test_char_table()

    def create_detailed_test_char_table(self):
        """创建详细的测试字表"""
        test_chars = {
            "今": {
                "词性": ["名", "副"], 
                "词性字义": "现在、当前、今天",
                "现代义": "现代用法与古代基本一致",
                "比喻义": "比喻当下，如'今非昔比'",
                "情感色彩": "中性"
            },
            "天": {
                "词性": ["名", "形"], 
                "词性字义": "天空",
                "现代义": "天空、天气",
                "比喻义": "比喻自然、上帝等",
                "情感色彩": "中性"
            },
            "气": {
                "词性": ["名", "动", "形"], 
                "词性字义": "气体、空气、精神",
                "现代义": "气候、气息",
                "比喻义": "气质、气势",
                "情感色彩": "中性"
            },
            "真": {
                "词性": ["形", "副", "名", "动"], 
                "词性字义": "真实",
                "现代义": "确实、真正",
                "比喻义": "真诚、真实",
                "情感色彩": "中性"
            },
            "好": {
                "词性": ["形", "副", "动", "名"], 
                "词性字义": "优点多、友好",
                "现代义": "良好、美好",
                "比喻义": "合适、完善",
                "情感色彩": "积极"
            },
            "啊": {
                "词性": ["叹", "助"], 
                "词性字义": "语气词",
                "现代义": "表示各种语气",
                "比喻义": "",
                "情感色彩": "中性"
            },
            "是": {
                "词性": ["动"], 
                "词性字义": "肯定、判断",
                "现代义": "是、对",
                "比喻义": "",
                "情感色彩": "中性"
            }
        }
        return test_chars

    def convert_char_format(self, char_info: Dict) -> Dict:
        """转换字符格式"""
        return {
            "词性": char_info.get("词性", ["名"]),
            "词性字义": char_info.get("词性字义", ""),
            "现代义": char_info.get("现代义", ""),
            "比喻义": char_info.get("比喻义", ""),
            "情感色彩": char_info.get("情感色彩", "中性")
        }

    def get_char_info(self, char: str) -> Dict[str, Any]:
        """获取字符信息"""
        return self.char_table.get(char, {
            "词性": ["名"], 
            "词性字义": char, 
            "现代义": char, 
            "比喻义": "",
            "情感色彩": "中性"
        })

    def step1_parse_sentence(self, sentence: str) -> List[Dict]:
        """步骤1：解析句子，获取每个字的词性"""
        result = []
        for i, char in enumerate(sentence):
            char_info = self.get_char_info(char)
            result.append({
                "字": char,
                "位置": i,
                "词性列表": char_info.get("词性", ["名"]),
                "词性字义": char_info.get("词性字义", ""),
                "现代义": char_info.get("现代义", ""),
                "比喻义": char_info.get("比喻义", ""),
                "情感色彩": char_info.get("情感色彩", "中性")
            })
        return result

    def step2_generate_pos_combinations(self, parsed_sentence: List[Dict]) -> List[List[Tuple]]:
        """步骤2：生成所有可能的词性组合"""
        pos_lists = [char["词性列表"] for char in parsed_sentence]
        
        def generate_combinations(current, index):
            if index == len(pos_lists):
                return [current]
            
            combinations = []
            for pos in pos_lists[index]:
                new_combo = current + [(parsed_sentence[index]["字"], pos)]
                combinations.extend(generate_combinations(new_combo, index + 1))
            return combinations
        
        return generate_combinations([], 0)

    def step3_identify_structures(self, pos_combination: List[Tuple]) -> Dict[str, List]:
        """步骤3：识别各种句子结构"""
        structures = {
            "定中结构": [],
            "动宾结构": [],
            "并列结构": [],
            "补充结构": [],
            "主谓结构": [],
            "助词结构": []
        }
        
        chars = [item[0] for item in pos_combination]
        pos_seq = [item[1] for item in pos_combination]
        
        # 识别定中结构：名 + 名
        for i in range(len(pos_seq) - 1):
            if pos_seq[i] in ["名", "时间", "处所", "形", "区别"] and pos_seq[i+1] == "名":
                structures["定中结构"].append((i, i+1))
        
        # 识别主谓结构：名 + 动/形
        for i in range(len(pos_seq) - 1):
            if pos_seq[i] == "名" and pos_seq[i+1] in ["动", "形"]:
                structures["主谓结构"].append((i, i+1))
        
        # 识别助词结构：实词 + 助词
        for i in range(len(pos_seq) - 1):
            if pos_seq[i] in ["名", "动", "形", "副"] and pos_seq[i+1] in ["助", "语气"]:
                structures["助词结构"].append((i, i+1))
        
        # 识别补充结构：动 + 形 + 助
        for i in range(len(pos_seq) - 2):
            if pos_seq[i] == "动" and pos_seq[i+1] == "形" and pos_seq[i+2] in ["助", "语气"]:
                structures["补充结构"].append((i, i+1, i+2))
        
        return structures

    def step4_apply_redline_rules(self, structures: Dict[str, List], pos_combination: List[Tuple]) -> Dict[str, List]:
        """步骤4：应用红线规则过滤无效组合"""
        filtered_structures = {key: [] for key in structures.keys()}
        pos_seq = [item[1] for item in pos_combination]
        
        # 应用基本的红线规则
        for struct_type, struct_list in structures.items():
            for struct in struct_list:
                if self.is_structure_valid(struct_type, struct, pos_seq):
                    filtered_structures[struct_type].append(struct)
        
        return filtered_structures

    def is_structure_valid(self, struct_type: str, struct: tuple, pos_seq: List[str]) -> bool:
        """检查结构是否有效"""
        # 简单的红线规则检查
        if struct_type == "定中结构":
            i, j = struct
            return pos_seq[j] == "名"  # 定中结构的核心必须是名词
        
        elif struct_type == "主谓结构":
            i, j = struct
            return pos_seq[i] == "名" and pos_seq[j] in ["动", "形"]
        
        elif struct_type == "助词结构":
            i, j = struct
            return pos_seq[j] in ["助", "语气"] and j == len(pos_seq) - 1  # 助词必须在句末
        
        return True

    def step5_identify_function_blocks(self, filtered_structures: Dict[str, List], 
                                     pos_combination: List[Tuple]) -> List[str]:
        """步骤5：识别功能块"""
        blocks = []
        pos_seq = [item[1] for item in pos_combination]
        chars = [item[0] for item in pos_combination]
        
        # 识别话题块（句首的时间词、名词等）
        if len(pos_seq) > 0 and pos_seq[0] in ["时间", "处所", "名"]:
            # 检查是否符合定中结构
            topic_indices = []
            for i in range(min(3, len(pos_seq))):  # 话题一般在前3个字
                if pos_seq[i] in ["时间", "处所", "名", "形", "区别"]:
                    topic_indices.append(i)
                else:
                    break
            if topic_indices:
                blocks.append("话题")
        
        # 识别评述块（包含动作或状态描述）
        has_action_or_state = any(pos in ["动", "形", "副"] for pos in pos_seq)
        if has_action_or_state:
            blocks.append("评述")
        
        # 识别感叹块（句末语气词）
        if len(pos_seq) > 0 and pos_seq[-1] in ["叹", "语气", "助"]:
            blocks.append("感叹")
        
        return blocks

    def step6_generate_response_structure(self, blocks: List[str], 
                                        filtered_structures: Dict[str, List],
                                        pos_combination: List[Tuple]) -> str:
        """步骤6：生成回复结构"""
        if not blocks:
            return "嗯。"
        
        # 选择呼应词
        echo_word = random.choice(self.echo_words)
        
        # 根据功能块组合选择回复模板
        if "话题" in blocks and "评述" in blocks and "感叹" in blocks:
            # 完整结构：呼应 + 话题 + 评述 + 感叹
            topic_content = self.extract_content_by_pos(pos_combination, ["时间", "处所", "名"])
            comment_content = self.extract_content_by_pos(pos_combination, ["动", "形", "副"])
            exclamation_content = self.extract_content_by_pos(pos_combination, ["叹", "语气", "助"])
            
            if topic_content and comment_content:
                response = f"{echo_word}，{topic_content}{comment_content}{exclamation_content if exclamation_content else '！'}"
            else:
                response = f"{echo_word}！"
                
        elif "话题" in blocks and "评述" in blocks:
            # 话题+评述结构
            topic_content = self.extract_content_by_pos(pos_combination, ["时间", "处所", "名"])
            comment_content = self.extract_content_by_pos(pos_combination, ["动", "形", "副"])
            
            if topic_content and comment_content:
                response = f"{echo_word}，{topic_content}{comment_content}。"
            else:
                response = f"{echo_word}。"
                
        elif "评述" in blocks:
            # 只有评述
            comment_content = self.extract_content_by_pos(pos_combination, ["动", "形", "副"])
            response = f"{echo_word}，{comment_content}。" if comment_content else f"{echo_word}。"
            
        else:
            # 默认回复
            response = f"{echo_word}。"
        
        return response

    def extract_content_by_pos(self, pos_combination: List[Tuple], target_pos: List[str]) -> str:
        """根据词性提取内容"""
        content = []
        for char, pos in pos_combination:
            if pos in target_pos:
                content.append(char)
        return "".join(content)

    def step7_add_punctuation(self, response: str, user_sentence: str) -> str:
        """步骤7：添加正确的标点符号"""
        # 确保有标点结尾
        if not response or response[-1] not in "。！？":
            if any(q in user_sentence for q in ["吗", "呢", "么", "？"]):
                response = response + "？"
            elif any(word in user_sentence for word in ["真", "太", "好", "美", "！"]):
                response = response + "！"
            else:
                response = response + "。"
        
        # 在呼应词后添加逗号（如果句子较长）
        for echo_word in self.echo_words:
            if response.startswith(echo_word) and len(response) > len(echo_word) + 2:
                if "，" not in response[len(echo_word):len(echo_word)+2]:
                    response = response.replace(echo_word, echo_word + "，", 1)
                    break
        
        return response

    def process_user_input(self, user_sentence: str) -> str:
        """严格按照7个步骤处理用户输入"""
        print(f"\n=== 处理用户输入: '{user_sentence}' ===")
        
        try:
            # 步骤1：解析句子，获取每个字的词性
            parsed_sentence = self.step1_parse_sentence(user_sentence)
            print(f"步骤1完成 - 解析出{len(parsed_sentence)}个字符")
            
            # 步骤2：生成所有可能的词性组合
            pos_combinations = self.step2_generate_pos_combinations(parsed_sentence)
            print(f"步骤2完成 - 生成{len(pos_combinations)}种词性组合")
            
            if not pos_combinations:
                return "输入无法解析"
            
            # 选择第一个组合进行处理（实际应该选择最优组合）
            selected_combination = pos_combinations[0]
            print(f"选择的词性组合: {selected_combination}")
            
            # 步骤3：识别各种句子结构
            structures = self.step3_identify_structures(selected_combination)
            print(f"步骤3完成 - 识别出的结构: {structures}")
            
            # 步骤4：应用红线规则过滤
            filtered_structures = self.step4_apply_redline_rules(structures, selected_combination)
            print(f"步骤4完成 - 过滤后的结构: {filtered_structures}")
            
            # 步骤5：识别功能块
            function_blocks = self.step5_identify_function_blocks(filtered_structures, selected_combination)
            print(f"步骤5完成 - 识别的功能块: {function_blocks}")
            
            # 步骤6：生成回复结构
            response_structure = self.step6_generate_response_structure(function_blocks, filtered_structures, selected_combination)
            print(f"步骤6完成 - 生成的回复结构: '{response_structure}'")
            
            # 步骤7：添加正确的标点符号
            final_response = self.step7_add_punctuation(response_structure, user_sentence)
            print(f"步骤7完成 - 最终回复: '{final_response}'")
            
            print("=== 处理完成 ===\n")
            return final_response
            
        except Exception as e:
            print(f"处理过程中出现错误: {e}")
            return "嗯，让我想想..."

class StrictRuleBasedChatApplication:
    def __init__(self, root):
        self.root = root
        self.root.title("严格规则版汉语对话系统")
        self.root.geometry("800x600")
        
        # 初始化处理器
        self.processor = StrictRuleBasedProcessor(
            r"C:\Users\XUNXI\Desktop\QSFWF-XL-G2\新建文件夹 (2)\二进制\字表2.pkl"
        )
        
        self.create_widgets()
        
    def create_widgets(self):
        # 标题
        title_label = tk.Label(self.root, text="严格规则版汉语对话系统（7步处理流程）", 
                              font=("Arial", 14, "bold"))
        title_label.pack(pady=10)
        
        # 说明文字
        desc_label = tk.Label(self.root, text="严格按照7步流程处理：词性分析→结构识别→红线过滤→功能块识别→回复生成→标点校正", 
                             font=("Arial", 10), wraplength=600)
        desc_label.pack(pady=5)
        
        # 对话显示区域
        self.conversation_text = scrolledtext.ScrolledText(
            self.root, width=80, height=20, font=("Arial", 11)
        )
        self.conversation_text.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        self.conversation_text.config(state=tk.DISABLED)
        
        # 输入区域
        input_frame = tk.Frame(self.root)
        input_frame.pack(padx=10, pady=10, fill=tk.X)
        
        input_label = tk.Label(input_frame, text="输入:", font=("Arial", 12))
        input_label.pack(side=tk.LEFT)
        
        self.input_entry = tk.Entry(input_frame, width=60, font=("Arial", 12))
        self.input_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        self.input_entry.bind("<Return>", lambda event: self.send_message())
        
        send_button = tk.Button(input_frame, text="发送", command=self.send_message, 
                               font=("Arial", 12), bg="#4CAF50", fg="white")
        send_button.pack(side=tk.RIGHT, padx=5)
        
        clear_button = tk.Button(input_frame, text="清空", command=self.clear_conversation, 
                                font=("Arial", 12), bg="#f44336", fg="white")
        clear_button.pack(side=tk.RIGHT, padx=5)
        
        # 状态显示
        self.status_label = tk.Label(self.root, text="系统就绪", font=("Arial", 10), 
                                    fg="green")
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.add_message("系统", "欢迎使用严格规则版汉语对话系统！系统将严格按照7步流程处理您的输入。")

    def add_message(self, sender: str, message: str):
        self.conversation_text.config(state=tk.NORMAL)
        import datetime
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        
        if sender == "系统":
            prefix = f"[{timestamp}] 🤖 {sender}: "
            self.conversation_text.insert(tk.END, prefix, "system")
        else:
            prefix = f"[{timestamp}] 👤 {sender}: "
            self.conversation_text.insert(tk.END, prefix, "user")
            
        self.conversation_text.insert(tk.END, message + "\n")
        self.conversation_text.see(tk.END)
        self.conversation_text.config(state=tk.DISABLED)
        
        self.conversation_text.tag_config("system", foreground="blue")
        self.conversation_text.tag_config("user", foreground="green")
    
    def send_message(self):
        user_input = self.input_entry.get().strip()
        
        if not user_input:
            messagebox.showwarning("输入错误", "请输入消息")
            return
        
        self.add_message("用户", user_input)
        self.input_entry.delete(0, tk.END)
        
        self.status_label.config(text="处理中...", fg="orange")
        self.root.update()
        
        try:
            response = self.processor.process_user_input(user_input)
            self.add_message("系统", response)
            self.status_label.config(text="系统就绪", fg="green")
        except Exception as e:
            error_msg = f"处理错误: {str(e)}"
            self.add_message("系统", error_msg)
            self.status_label.config(text="错误", fg="red")
    
    def clear_conversation(self):
        self.conversation_text.config(state=tk.NORMAL)
        self.conversation_text.delete(1.0, tk.END)
        self.conversation_text.config(state=tk.DISABLED)
        self.add_message("系统", "对话记录已清空")
        self.status_label.config(text="系统就绪", fg="green")

def main():
    root = tk.Tk()
    app = StrictRuleBasedChatApplication(root)
    root.mainloop()

if __name__ == "__main__":
    main()