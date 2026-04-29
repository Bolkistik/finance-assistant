export function formatCurrency(amount) {
    return `${amount?.toLocaleString() || 0} rub`;
}

export function formatDate(date) {
    return new Date(date).toLocaleDateString('ru-RU');
}