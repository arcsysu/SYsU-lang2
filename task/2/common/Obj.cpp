#include "Obj.hpp"

void
Obj::Mgr::gc()
{
  // 标记可达对象
  gc_mark_dfs(this);

  // 清扫不可达对象
  Obj* here = this;
  while (true) {
    gc_unmark(here);
    auto next = here->__next__;
    if (next == this)
      break;

    if (!gc_marked(next))
      here->__next__ = next->__next__, delete next;
    else
      here = next;
  }
}

void
Obj::Mgr::__mark__(Mark mark)
{
  mark(mRoot);
}

void
Obj::Mgr::gc_mark_dfs(Obj* obj)
{
  if (obj == nullptr || gc_marked(obj))
    return;
  gc_mark(obj), obj->__mark__(&gc_mark_dfs);
}
