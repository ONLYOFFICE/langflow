from dataclasses import dataclass
from time import sleep
from typing import Callable, ParamSpec, Tuple
from .client import ErrorResponse, Operation, Response


@dataclass
class _State:
    id: str
    done: bool | None
    error: Exception | None


ListOperationsFunc = Callable[[], Tuple[list[Operation], Response]]

P = ParamSpec("P")
AsyncOperationFunc = Callable[P, Tuple[Operation | list[Operation], Response]]


class Syncer:
    def __init__(
        self,
        list: ListOperationsFunc,
        func: AsyncOperationFunc[P],
        *args: P.args,
        **kwargs: P.kwargs,
    ):
        self._list = list
        self._delay = 100 / 1000 # 100ms
        self._limit = 100
        self._func = func
        self._func_args = args
        self._func_kwargs = kwargs


    def do(self) -> None:
        try:
            ops, res = self._func(*self._func_args, **self._func_kwargs)
            if isinstance(res, ErrorResponse):
                raise res.exception
        except Exception as err:
            raise ValueError("Calling async operation") from err

        map: dict[str, _State] = {}

        if isinstance(ops, list):
            for op in ops:
                map[op.id] = _State(op.id, op.error, _is_finished(op))
        else:
            map[ops.id] = _State(ops.id, ops.error, _is_finished(ops))

        if not map:
            raise ValueError("No operations to wait for")

        while self._limit > 0:
            try:
                ops, res = self._list()
                if isinstance(res, ErrorResponse):
                    raise res.exception
            except Exception as err:
                raise ValueError("Listing active operations") from err

            for op in ops:
                if op.id not in map:
                    continue

                try:
                    if op.error:
                        raise ValueError(f"Operation {op.id} failed") from Exception(op.error)
                except Exception as err:
                    map[op.id].error = err

                if map[op.id].error:
                    map[op.id].done = True
                else:
                    map[op.id].done = _is_finished(op)

            done = True

            for _, st in map.items():
                if not st.done:
                    done = False
                    break

            if done:
                break

            self._limit -= 1
            sleep(self._delay)

        errs: list[Exception] = []
        done = True

        for _, st in map.items():
            if st.error:
                errs.append(st.error)

            if not st.done:
                done = False

        if errs:
            raise ExceptionGroup("Multiple errors while waiting for operations", errs)

        if not done:
            raise ValueError("Operations did not finish in time")


def _is_finished(op: Operation) -> bool:
    return op.finished or op.progress == 100 or op.percents == 100
