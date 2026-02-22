
from sub_answer import AIAnswerGenerator
from config import API_CONFIG, CURRENT_API, RUN_CONFIG

def main():
    """主函数"""
    print("=" * 70)
    print("AI答题生成器 - 快速启动")
    print("=" * 70)
    
    # 从配置文件获取API信息
    api_info = API_CONFIG[CURRENT_API]
    
    print(f"当前API: {CURRENT_API}")
    print(f"模型: {api_info['model']}")
    print("=" * 70)
    
    # 创建生成器
    generator = AIAnswerGenerator(
        api_url=api_info['url'],
        api_key=api_info['key'],
        model_name=api_info['model']
    )
    
    # 运行
    try:
        generator.run()
    except KeyboardInterrupt:
        print("\n\n程序被用户中断")
    except Exception as e:
        print(f"\n\n程序运行出错: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()