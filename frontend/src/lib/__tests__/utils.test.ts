import { cn, formatBytes, formatDate } from "@/lib/utils";

describe("cn", () => {
  it("merges class names and resolves Tailwind conflicts", () => {
    expect(cn("px-2", "px-4")).toBe("px-4");
  });

  it("drops falsy values", () => {
    expect(cn("a", false, undefined, "b")).toBe("a b");
  });
});

describe("formatBytes", () => {
  it("formats bytes under 1024 as-is", () => {
    expect(formatBytes(500)).toBe("500 B");
  });

  it("formats kilobytes", () => {
    expect(formatBytes(2048)).toBe("2.0 KB");
  });

  it("formats megabytes", () => {
    expect(formatBytes(5 * 1024 * 1024)).toBe("5.0 MB");
  });
});

describe("formatDate", () => {
  it("formats an ISO date into a readable string", () => {
    const result = formatDate("2026-01-15T00:00:00Z");
    expect(result).toMatch(/2026/);
    expect(result).toMatch(/Jan/);
  });
});
