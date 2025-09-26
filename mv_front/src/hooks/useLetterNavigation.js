import { useMemo, useRef, createRef } from "react";

export const useLetterNavigation = (filteredCollections = []) => {
    // 1. Формуємо список букв: беремо першу букву з усіх імен карток, латиниця вище кирилиці
    // Формуємо список букв у тому ж порядку, як і картки (без сортування)
    const letters = useMemo(() => {
        const result = [];
        const seen = new Set();
        filteredCollections.forEach(item => {
            const first = item.title?.trim()?.[0]?.toUpperCase();
            if (first && !seen.has(first)) {
            result.push(first);
            seen.add(first);
            }
        });
        return result;
    }, [filteredCollections]);

    // 2. Створюємо ref для кожної букви
    const letterRefs = useRef({});
    filteredCollections.forEach(item => {
        const first = item.title?.[0]?.toUpperCase();
        if (first && !letterRefs.current[first]) {
            letterRefs.current[first] = createRef();
        }
    });

    // 3. Функція скролу
    const scrollToLetter = (letter) => {
        const ref = letterRefs.current[letter];
        if (ref && ref.current) {
            ref.current.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
    };

    return {letters, letterRefs, scrollToLetter}
}