import type { ReactElement, ReactNode } from "react";

export type TableColumn<T> = {
  key: string;
  header: string;
  mono?: boolean;
  render?: (row: T) => ReactNode;
};

type TableProps<T> = {
  columns: Array<TableColumn<T>>;
  rows: T[];
  getRowKey: (row: T) => string;
};

export function Table<T>({ columns, rows, getRowKey }: TableProps<T>): ReactElement {
  return (
    <div className="table-wrap">
      <table className="table">
        <thead>
          <tr>
            {columns.map((column) => (
              <th key={column.key} className={column.mono === true ? "table__cell--mono" : undefined}>
                {column.header}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row) => (
            <tr key={getRowKey(row)}>
              {columns.map((column) => (
                <td key={column.key} className={column.mono === true ? "table__cell--mono" : undefined}>
                  {column.render !== undefined ? column.render(row) : String((row as Record<string, unknown>)[column.key] ?? "")}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
