import os
import sys
import importlib.util
import inspect
from abc import ABC, abstractmethod


class PluginInterface(ABC):
    """插件接口基类"""
    
    @property
    @abstractmethod
    def name(self):
        """插件名称"""
        pass
    
    @property
    @abstractmethod
    def version(self):
        """插件版本"""
        pass
    
    @property
    @abstractmethod
    def description(self):
        """插件描述"""
        pass
    
    @abstractmethod
    def initialize(self, main_window):
        """初始化插件"""
        pass
    
    @abstractmethod
    def finalize(self):
        """清理插件资源"""
        pass


class PluginManager:
    """插件管理器"""
    
    def __init__(self, plugins_dir="plugins"):
        self.plugins_dir = plugins_dir
        self.loaded_plugins = {}
        self.main_window = None
        
        # 确保插件目录存在
        if not os.path.exists(self.plugins_dir):
            os.makedirs(self.plugins_dir)
            
    def set_main_window(self, main_window):
        """设置主窗口引用"""
        self.main_window = main_window
        
    def load_plugins(self):
        """加载所有插件"""
        if not os.path.exists(self.plugins_dir):
            return
            
        for filename in os.listdir(self.plugins_dir):
            if filename.endswith('.py') and not filename.startswith('_'):
                plugin_path = os.path.join(self.plugins_dir, filename)
                self.load_plugin(plugin_path)
                
    def load_plugin(self, plugin_path):
        """加载单个插件"""
        try:
            # 获取插件模块名
            plugin_name = os.path.splitext(os.path.basename(plugin_path))[0]
            
            # 动态导入插件模块
            spec = importlib.util.spec_from_file_location(plugin_name, plugin_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # 查找插件类
            plugin_classes = []
            for name, obj in inspect.getmembers(module):
                if (inspect.isclass(obj) and 
                    issubclass(obj, PluginInterface) and 
                    obj != PluginInterface):
                    plugin_classes.append(obj)
                    
            # 实例化并初始化插件
            for plugin_class in plugin_classes:
                plugin_instance = plugin_class()
                if self.main_window:
                    plugin_instance.initialize(self.main_window)
                self.loaded_plugins[plugin_instance.name] = plugin_instance
                print(f"插件已加载: {plugin_instance.name} v{plugin_instance.version}")
                
        except Exception as e:
            print(f"加载插件失败 {plugin_path}: {e}")
            
    def unload_plugin(self, plugin_name):
        """卸载插件"""
        if plugin_name in self.loaded_plugins:
            plugin = self.loaded_plugins[plugin_name]
            try:
                plugin.finalize()
                del self.loaded_plugins[plugin_name]
                print(f"插件已卸载: {plugin_name}")
            except Exception as e:
                print(f"卸载插件失败 {plugin_name}: {e}")
                
    def get_loaded_plugins(self):
        """获取已加载的插件列表"""
        return list(self.loaded_plugins.keys())
        
    def get_plugin(self, plugin_name):
        """获取指定插件实例"""
        return self.loaded_plugins.get(plugin_name)
        
    def reload_plugin(self, plugin_name):
        """重新加载插件"""
        # 这里可以实现插件热重载逻辑
        pass
        
    def finalize_all(self):
        """清理所有插件"""
        for plugin_name in list(self.loaded_plugins.keys()):
            self.unload_plugin(plugin_name)
