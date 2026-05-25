import { fireEvent, render, screen } from "@testing-library/react";
import Calendar from "../../src/components/Calendar.jsx";

beforeEach(() => {
  vi.useFakeTimers();
  vi.setSystemTime(new Date("2026-05-25T12:00:00-04:00"));
});

afterEach(() => {
  vi.useRealTimers();
});

test("only future available dates are selectable", async () => {
  const onSelect = vi.fn();

  render(
    <Calendar
      available={{
        "2026-05-10": [{ id: 1 }],
        "2026-05-26": [{ id: 2 }],
      }}
      selected=""
      onSelect={onSelect}
    />
  );

  expect(screen.getByText("May 2026")).toBeInTheDocument();
  expect(screen.queryByRole("button", { name: "10" })).not.toBeInTheDocument();

  fireEvent.click(screen.getByRole("button", { name: "26" }));

  expect(onSelect).toHaveBeenCalledWith("2026-05-26");
});

test("moves between months and marks the selected date", async () => {
  const onSelect = vi.fn();

  render(
    <Calendar
      available={{ "2026-06-03": [{ id: 3 }] }}
      selected="2026-06-03"
      onSelect={onSelect}
    />
  );

  fireEvent.click(screen.getByRole("button", { name: "Next month" }));

  expect(screen.getByText("June 2026")).toBeInTheDocument();
  const selectedDate = screen.getByRole("button", { name: "3" });
  expect(selectedDate).toHaveAttribute("aria-pressed", "true");

  fireEvent.click(selectedDate);

  expect(onSelect).toHaveBeenCalledWith("2026-06-03");
});
