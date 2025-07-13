import json
import os
from datetime import datetime


class BookmarkManager:
    """书签管理器"""
    
    def __init__(self, bookmarks_file="bookmarks.json"):
        self.bookmarks_file = bookmarks_file
        self.bookmarks = []
        self.load_bookmarks()
        
    def load_bookmarks(self):
        """加载书签"""
        if os.path.exists(self.bookmarks_file):
            try:
                with open(self.bookmarks_file, 'r', encoding='utf-8') as f:
                    self.bookmarks = json.load(f)
            except Exception as e:
                print(f"加载书签失败: {e}")
                self.bookmarks = []
        else:
            self.bookmarks = []
            
    def save_bookmarks(self):
        """保存书签"""
        try:
            with open(self.bookmarks_file, 'w', encoding='utf-8') as f:
                json.dump(self.bookmarks, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存书签失败: {e}")
            
    def add_bookmark(self, title, page, file_path=None):
        """添加书签"""
        bookmark = {
            'title': title,
            'page': page,
            'file_path': file_path,
            'created_time': datetime.now().isoformat(),
            'id': len(self.bookmarks)
        }
        self.bookmarks.append(bookmark)
        self.save_bookmarks()
        
    def remove_bookmark(self, bookmark_id):
        """删除书签"""
        self.bookmarks = [b for b in self.bookmarks if b.get('id') != bookmark_id]
        # 重新分配ID
        for i, bookmark in enumerate(self.bookmarks):
            bookmark['id'] = i
        self.save_bookmarks()
        
    def get_bookmarks(self, file_path=None):
        """获取书签列表"""
        if file_path:
            return [b for b in self.bookmarks if b.get('file_path') == file_path]
        return self.bookmarks
        
    def clear_bookmarks(self):
        """清空所有书签"""
        self.bookmarks = []
        self.save_bookmarks()
        
    def update_bookmark(self, bookmark_id, title=None, page=None):
        """更新书签"""
        for bookmark in self.bookmarks:
            if bookmark.get('id') == bookmark_id:
                if title is not None:
                    bookmark['title'] = title
                if page is not None:
                    bookmark['page'] = page
                bookmark['modified_time'] = datetime.now().isoformat()
                break
        self.save_bookmarks()
