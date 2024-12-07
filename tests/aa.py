class LibraryError(Exception):
    """图书馆通用异常"""
    pass

class BookNotFoundError(LibraryError):
    """图书未找到异常"""
    def __init__(self, title):
        super().__init__(f"图书未找到：{title}")
        self.title = title

class BookAlreadyExistsError(LibraryError):
    """图书已存在异常"""
    def __init__(self, title):
        super().__init__(f"图书已存在：{title}")
        self.title = title

class InvalidBookError(LibraryError):
    """无效图书异常"""
    def __init__(self, title, reason):
        super().__init__(f"无效图书：{title}，原因：{reason}")
        self.title = title
        self.reason = reason

class Book:
    def __init__(self, title, author, year):
        self.title = title
        self.author = author
        self.year = year

class Library:
    def __init__(self):
        self.books = {}

    def add_book(self, book):
        if book.title in self.books:
            raise BookAlreadyExistsError(book.title)
        if not book.title or not book.author or not book.year:
            raise InvalidBookError(book.title, "信息不完整")
        self.books[book.title] = book

    def remove_book(self, title):
        if title not in self.books:
            raise BookNotFoundError(title)
        del self.books[title]

    def get_book(self, title):
        if title not in self.books:
            raise BookNotFoundError(title)
        return self.books[title]

    def list_books(self):
        return list(self.books.values())

def log_activity(func):
    def wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
            return result
        except LibraryError as e:
            print(f"图书馆操作异常：{e}")
            return None
    return wrapper

@log_activity
def main():
    library = Library()

    # 添加图书
    # try:
    #     book1 = Book("Python编程", "Guido van Rossum", 2020)
    #     library.add_book(book1)
    # except LibraryError as e:
    #     print(f"添加图书时发生异常：{e}")
    #     print(f"添加图书时发生异常：{e.args}")

    try:
        book2 = Book("", "Unknown Author", 2021)
        library.add_book(book2)
    except LibraryError as e:
        print(f"添加图书时发生异常：{e}")
        print(f"添加图书时发生异常#：{e.args}")


    # 列出图书
    # print("当前图书列表：")
    # for book in library.list_books():
    #     print(f"标题：{book.title}, 作者：{book.author}, 出版年份：{book.year}")
    #
    # # 获取图书
    # try:
    #     book = library.get_book("Python编程")
    #     print(f"获取图书：标题：{book.title}, 作者：{book.author}, 出版年份：{book.year}")
    # except LibraryError as e:
    #     print(f"获取图书时发生异常：{e}")
    #
    # try:
    #     book = library.get_book("Java编程")
    #     print(f"获取图书：标题：{book.title}, 作者：{book.author}, 出版年份：{book.year}")
    # except LibraryError as e:
    #     print(f"获取图书时发生异常：{e}")
    #
    # # 删除图书
    # try:
    #     library.remove_book("Python编程")
    #     print("图书'Python编程'已删除")
    # except LibraryError as e:
    #     print(f"删除图书时发生异常：{e}")
    #
    # try:
    #     library.remove_book("Java编程")
    #     print("图书'Java编程'已删除")
    # except LibraryError as e:
    #     print(f"删除图书时发生异常：{e}")

if __name__ == "__main__":
    main()

