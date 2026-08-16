import { render, screen, fireEvent } from "@testing-library/react";
import { Button } from "@/components/ui/button";
import { ConfidenceBadge } from "@/components/ui/card";

describe("Button", () => {
  it("renders children and responds to clicks", () => {
    const handleClick = jest.fn();
    render(<Button onClick={handleClick}>Click me</Button>);
    fireEvent.click(screen.getByText("Click me"));
    expect(handleClick).toHaveBeenCalledTimes(1);
  });

  it("is disabled when the disabled prop is set", () => {
    render(<Button disabled>Disabled</Button>);
    expect(screen.getByText("Disabled")).toBeDisabled();
  });
});

describe("ConfidenceBadge", () => {
  it("shows high-confidence styling for scores >= 0.7", () => {
    render(<ConfidenceBadge score={0.94} />);
    expect(screen.getByText("94% match")).toBeInTheDocument();
  });

  it("shows the rounded percentage for a mid-range score", () => {
    render(<ConfidenceBadge score={0.5} />);
    expect(screen.getByText("50% match")).toBeInTheDocument();
  });

  it("shows the rounded percentage for a low score", () => {
    render(<ConfidenceBadge score={0.12} />);
    expect(screen.getByText("12% match")).toBeInTheDocument();
  });
});
