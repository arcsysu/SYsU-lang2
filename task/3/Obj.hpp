#pragma once

#include <cassert>
#include <cstdio>
#include <cstdlib>
#include <memory>
#include <vector>

/// 错误断言，打印文件和行号，方便定位问题。
#define ASSERT(expr)                                                           \
  ((expr) || (fprintf(stderr, "asserted at %s:%d\n", __FILE__, __LINE__),      \
              abort(),                                                         \
              false))

/// 错误中断，打印文件和行号，方便定位问题。
#define ABORT()                                                                \
  (fprintf(stderr, "aborted at %s:%d\n", __FILE__, __LINE__), abort())

/// 对象系统基类
struct alignas(ptrdiff_t) Obj
{
  struct Mgr;
  struct Walked;

  using Mark = void (*)(Obj* obj);

  Obj() = default;
  virtual ~Obj() = default;

  template<typename T>
  T* dcst()
  {
    return dynamic_cast<T*>(this);
  }

  template<typename T>
  T* dcst() const
  {
    return dynamic_cast<T*>(this);
  }

  template<typename T>
  T* scst()
  {
    return static_cast<T*>(this);
  }

  template<typename T>
  T* scst() const
  {
    return static_cast<T*>(this);
  }

  template<typename T>
  T& rcst()
  {
    return *reinterpret_cast<T*>(this);
  }

  template<typename T>
  T& rcst() const
  {
    return *reinterpret_cast<T*>(this);
  }

  void* any{ nullptr }; /// 留给遍历器存放任意数据

  template<typename T>
  T* any_as()
  {
    return reinterpret_cast<T*>(any);
  }

  template<typename T>
  T* any_as() const
  {
    return reinterpret_cast<T*>(any);
  }

private:
  Obj(Obj* next)
    : __next__(next)
  {
  }

  Obj(const Obj&) = delete;
  Obj(Obj&&) = delete;
  void operator=(const Obj&) = delete;
  void operator=(Obj&&) = delete;

  Obj* __next__{ nullptr }; /// 环形指针，低3位由于对齐要求必为0，用作标记

  virtual void __mark__(Mark mark) = 0; /// 标记对象
};

/// 对象管理器
struct Obj::Mgr : Obj
{
  Mgr()
    : Obj(this)
  {
  }

  template<typename T,
           typename... Args,
           typename = std::enable_if_t<std::is_convertible_v<T*, Obj*>>>
  T* make(Args... args)
  {
    auto obj = new T(args...);
    obj->__next__ = __next__, __next__ = obj;
    return obj;
  }

  Obj* mRoot{ nullptr }; /// 根对象

  /// 垃圾回收，使用标记-清扫算法
  /// @warning 垃圾回收时调用栈上不能有对象的引用！
  void gc();

private:
  void __mark__(Mark mark) override;

  static bool gc_marked(const Obj* obj)
  {
    return reinterpret_cast<uintptr_t>(obj->__next__) & uintptr_t(0b1);
  }

  static void gc_unmark(Obj* obj)
  {
    reinterpret_cast<uintptr_t&>(obj->__next__) &= ~uintptr_t(0b1);
  }

  static void gc_mark(Obj* obj)
  {
    reinterpret_cast<uintptr_t&>(obj->__next__) |= uintptr_t(0b1);
  }

  static void gc_mark_dfs(Obj* obj);
};

/// 检查循环引用，防止无限递归。
struct Obj::Walked
{
  Obj* mObj;

  Walked(Obj* obj)
    : mObj(obj)
  {
    ASSERT((reinterpret_cast<uintptr_t>(mObj->__next__) & 0b10) == 0);
    reinterpret_cast<uintptr_t&>(mObj->__next__) |= uintptr_t(0b10);
  }

  ~Walked()
  {
    reinterpret_cast<uintptr_t&>(mObj->__next__) &= ~uintptr_t(0b10);
  }
};
