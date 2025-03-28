from collections.abc import Callable
from dataclasses import dataclass
from time import sleep
from typing import ParamSpec, overload

from .client import ErrorResponse, Operation, Response


@dataclass
class _State:
    id: str
    done: bool | None
    error: Exception | None


ListOperationsFunc = Callable[[], tuple[list[Operation], Response]]

P = ParamSpec("P")


class Syncer:
    def __init__(self, list: ListOperationsFunc):  # noqa: A002
        self._list = list
        self._delay = 100 / 1000  # 100ms
        self._limit = 100


    @overload
    def do(
        self,
        func: Callable[P, tuple[Operation, Response]],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> Operation:
        ...


    @overload
    def do(
        self,
        func: Callable[P, tuple[list[Operation], Response]],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> list[Operation]:
        ...


    def do(
        self,
        func: Callable[P, tuple[Operation | list[Operation], Response]],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> Operation | list[Operation]:
        try:
            ops, res = func(*args, **kwargs)
            if isinstance(res, ErrorResponse):
                raise res.exception
        except Exception as err:
            msg = "Calling async operation"
            raise ValueError(msg) from err

        return self.wait(ops)


    @overload
    def wait(self, ops: Operation) -> Operation:
        ...


    @overload
    def wait(self, ops: list[Operation]) -> list[Operation]: # type: ignore [overload-cannot-match]
        ...


    def wait(self, ops: Operation | list[Operation]) -> Operation | list[Operation]:
        states: dict[str, _State] = {}

        if isinstance(ops, list):
            for op in ops:
                states[op.id] = _State(op.id, _is_finished(op), op.error)
        else:
            states[ops.id] = _State(ops.id, _is_finished(ops), ops.error)

        if not states:
            msg = "No operations to wait for"
            raise ValueError(msg)

        results: dict[str, Operation] = {}

        limit = self._limit

        while limit > 0:
            try:
                ls, res = self._list()
                if isinstance(res, ErrorResponse):
                    raise res.exception
            except Exception as err:
                msg = "Listing active operations"
                raise ValueError(msg) from err

            for op in ls:
                if op.id not in states:
                    continue

                try:
                    if op.error:
                        msg = f"Operation {op.id} failed"
                        raise ValueError(msg) from Exception(op.error)
                except Exception as err:  # noqa: BLE001
                    states[op.id].error = err

                if states[op.id].error:
                    states[op.id].done = True
                else:
                    states[op.id].done = _is_finished(op)

                results[op.id] = op

            done = True

            for st in states.values():
                if not st.done:
                    done = False
                    break

            if done:
                break

            limit -= 1
            sleep(self._delay)

        errs: list[Exception] = []
        done = True

        for st in states.values():
            if st.error:
                errs.append(st.error)

            if not st.done:
                done = False

        if errs:
            msg = "Multiple errors while waiting for operations"
            raise ExceptionGroup(msg, errs)

        if not done:
            msg = "Operations did not finish in time"
            raise ValueError(msg)

        if isinstance(ops, list):
            return list(results.values())

        return results[ops.id]


def _is_finished(op: Operation) -> bool:
    return op.finished or op.progress == 100 or op.percents == 100  # noqa: PLR2004
