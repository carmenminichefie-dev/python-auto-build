import tkinter as tk
from tkinter import messagebox
import os
import sys

try:
    from PIL import Image, ImageDraw, ImageTk, ImageGrab
    HAS_PIL = True
except ImportError:
    HAS_PIL = False
    print("警告：未安装PIL库，保存图片功能将不可用")
    print("请运行: pip install pillow")

class AttributeAllocator:
    def __init__(self, root):
        self.root = root
        self.root.title("请填写您的指标")
        self.root.geometry("650x500")
        self.root.resizable(False, False)
        
        # 绑定关闭事件
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # 初始值设置
        self.total_points = 27
        # 修改：使用deficit_history列表记录每次失衡减少的量
        self.attributes = {
            "力量": {"value": 10, "deficit_history": []},
            "生命": {"value": 10, "deficit_history": []},
            "魅力": {"value": 10, "deficit_history": []},
            "敏捷": {"value": 10, "deficit_history": []},
            "智力": {"value": 10, "deficit_history": []},
            "感知": {"value": 10, "deficit_history": []}
        }
        
        # 创建界面
        self.create_widgets()
        self.update_display()
    
    def create_widgets(self):
        # 总点数显示
        points_frame = tk.Frame(self.root)
        points_frame.pack(pady=10)
        
        tk.Label(points_frame, text="剩余点数:", font=("Arial", 12, "bold")).pack(side=tk.LEFT)
        self.points_label = tk.Label(points_frame, text=str(self.total_points), 
                                   font=("Arial", 14, "bold"), fg="blue")
        self.points_label.pack(side=tk.LEFT, padx=5)
        
        # 创建两列属性框架
        columns_frame = tk.Frame(self.root)
        columns_frame.pack(pady=10, fill=tk.BOTH, expand=True)
        
        # 左列
        left_frame = tk.Frame(columns_frame)
        left_frame.pack(side=tk.LEFT, padx=20, fill=tk.BOTH, expand=True)
        
        # 右列
        right_frame = tk.Frame(columns_frame)
        right_frame.pack(side=tk.RIGHT, padx=20, fill=tk.BOTH, expand=True)
        
        # 为每个属性创建控件
        self.attribute_widgets = {}
        attribute_names = list(self.attributes.keys())
        
        for i, attr_name in enumerate(attribute_names):
            # 决定放在左列还是右列
            if i < 3:
                parent = left_frame
            else:
                parent = right_frame
                
            self.create_attribute_widget(parent, attr_name)
        
        # 保存按钮（只在有PIL时启用）
        self.save_btn = tk.Button(self.root, text="保存为图片", command=self.save_as_image,
                                bg="green", fg="white", font=("Arial", 12))
        self.save_btn.pack(pady=10)
        
        if not HAS_PIL:
            self.save_btn.config(state=tk.DISABLED, text="保存为图片 (需要安装Pillow)")
        
        # 退出按钮
        quit_btn = tk.Button(self.root, text="退出程序", command=self.on_closing,
                           bg="red", fg="white", font=("Arial", 10))
        quit_btn.pack(pady=5)
    
    def create_attribute_widget(self, parent, attr_name):
        frame = tk.Frame(parent)
        frame.pack(pady=8, fill=tk.X)
        
        # 属性名称
        name_label = tk.Label(frame, text=attr_name, width=8, font=("Arial", 10))
        name_label.pack(side=tk.LEFT)
        
        # 属性值显示
        value_var = tk.StringVar()
        value_label = tk.Label(frame, textvariable=value_var, width=4, 
                             font=("Arial", 10, "bold"), relief="sunken")
        value_label.pack(side=tk.LEFT, padx=5)
        
        # 按钮框架
        btn_frame = tk.Frame(frame)
        btn_frame.pack(side=tk.RIGHT)
        
        # 减号按钮
        minus_btn = tk.Button(btn_frame, text="-", width=3, 
                            command=lambda: self.decrement_attribute(attr_name))
        minus_btn.pack(side=tk.LEFT, padx=2)
        
        # 加号按钮
        plus_btn = tk.Button(btn_frame, text="+", width=3,
                           command=lambda: self.increment_attribute(attr_name))
        plus_btn.pack(side=tk.LEFT, padx=2)
        
        # 存储控件引用
        self.attribute_widgets[attr_name] = {
            "value_var": value_var,
            "minus_btn": minus_btn,
            "plus_btn": plus_btn
        }
    
    def increment_attribute(self, attr_name):
        if self.total_points <= 0:
            return
            
        attr = self.attributes[attr_name]
        current_value = attr["value"]
        
        # 如果当前值小于10且有失衡调换记录
        if current_value < 10 and attr["deficit_history"]:
            # 修改：获取最近一次的减少量，而不是恢复所有
            last_deficit = attr["deficit_history"][-1]
            # 计算实际恢复量（不超过10）
            actual_restore = min(last_deficit, 10 - current_value)
            
            # 恢复数值
            attr["value"] += actual_restore
            
            # 更新失衡记录
            if actual_restore == last_deficit:
                # 完全恢复了这次减少
                attr["deficit_history"].pop()
            else:
                # 部分恢复，更新记录
                attr["deficit_history"][-1] = last_deficit - actual_restore
            
            # 消耗1点
            self.total_points -= 1
        else:
            # 正常加点
            attr["value"] += 1
            self.total_points -= 1
        
        self.update_display()
    
    def decrement_attribute(self, attr_name):
        attr = self.attributes[attr_name]
        current_value = attr["value"]
        
        if current_value <= 10:
            # 特殊递减规则
            # 修改：使用deficit_history的长度来计算减少量
            decrement_amount = 2 + len(attr["deficit_history"])
                
            if current_value > decrement_amount:
                attr["value"] -= decrement_amount
                # 修改：记录这次失衡减少的量到历史列表
                attr["deficit_history"].append(decrement_amount)
                self.total_points += 1
            else:
                messagebox.showwarning("警告", f"{attr_name} 无法再减少了！")
                return
        else:
            # 正常递减
            attr["value"] -= 1
            self.total_points += 1
        
        self.update_display()
    
    def update_display(self):
        # 更新总点数显示
        self.points_label.config(text=str(self.total_points))
        
        # 更新每个属性的显示和按钮状态
        for attr_name, widgets in self.attribute_widgets.items():
            attr_data = self.attributes[attr_name]
            current_value = attr_data["value"]
            
            # 更新数值显示
            widgets["value_var"].set(str(current_value))
            
            # 更新加号按钮状态 - 根据总点数决定是否显示
            if self.total_points <= 0:
                widgets["plus_btn"].pack_forget()  # 隐藏加号按钮
            else:
                widgets["plus_btn"].pack(side=tk.LEFT, padx=2)  # 显示加号按钮
            
            # 检查减号按钮是否应该显示
            if current_value <= 10:
                # 修改：使用deficit_history的长度来计算减少量
                decrement_amount = 2 + len(attr_data["deficit_history"])
                    
                if current_value <= decrement_amount:
                    widgets["minus_btn"].config(state=tk.DISABLED)
                else:
                    widgets["minus_btn"].config(state=tk.NORMAL)
            else:
                widgets["minus_btn"].config(state=tk.NORMAL)
    
    def save_as_image(self):
        """将当前界面保存为PNG图片"""
        if not HAS_PIL:
            messagebox.showerror("错误", "请先安装Pillow库：pip install pillow")
            return
        
        try:
            self.root.update()
        
            # 简化截图：直接截取整个屏幕区域
            x = self.root.winfo_rootx()
            y = self.root.winfo_rooty()
            width = self.root.winfo_width()
            height = self.root.winfo_height()
        
            image = ImageGrab.grab(bbox=(x, y, x + width, y + height))
        
            desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
            filename = os.path.join(desktop_path, "attribute_allocation.png")
        
            image.save(filename, "PNG")
            messagebox.showinfo("成功", f"图片已保存到桌面: attribute_allocation.png")
    
        except Exception as e:
            messagebox.showerror("错误", f"保存图片时出错: {str(e)}")
    
    def on_closing(self):
        """处理窗口关闭事件"""
        if messagebox.askokcancel("退出", "确定要退出程序吗？"):
            self.root.destroy()
            sys.exit()

def main():
    try:
        root = tk.Tk()
        app = AttributeAllocator(root)
        root.mainloop()
    except Exception as e:
        print(f"程序运行出错: {e}")
        input("按Enter键退出...")

if __name__ == "__main__":
    main()
