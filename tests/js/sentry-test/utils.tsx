import MockDate from 'mockdate';

// Taken from https://stackoverflow.com/a/56859650/1015027
function findTextWithMarkup(contentNode: null | Element, textMatch: string | RegExp) {
  const hasText = (node: Element): boolean => {
    if (node.textContent === null) {
      return false;
    }
    if (typeof textMatch === 'string') {
      return node.textContent.includes(textMatch);
    }
    return textMatch.test(node.textContent);
  };

  const nodeHasText = hasText(contentNode as Element);
  const childrenDontHaveText = Array.from(contentNode?.children || []).every(
    child => !hasText(child)
  );
  return nodeHasText && childrenDontHaveText;
}

/**
 * May be used with a *ByText RTL matcher to match text within multiple nodes
 *
 * e.g.: <div>Hello <span>world</span></div>
 */
export function textWithMarkupMatcher(textMatch: string | RegExp) {
  return function (_: string, element: Element | null) {
    return findTextWithMarkup(element, textMatch);
  };
}

export function setMockDate(date: Date | number) {
  MockDate.set(date);
}

/**
 * Mock (current) date to always be National Pasta Day
 * 2017-10-17T02:41:20.000Z
 */
export function resetMockDate() {
  const constantDate = new Date(1508208080000);
  MockDate.set(constantDate);
}
