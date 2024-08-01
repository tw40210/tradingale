// Sample data: List of items and their corresponding API endpoints
const base_url = 'https://api.example.com'

const items = [
    { name: 'Item 1', apis: [['hh', `${base_url}/end1`], ['gg',`${base_url}/end2`]] },
];

document.addEventListener('DOMContentLoaded', () => {
    const itemsList = document.getElementById('itemsList');

    items.forEach(item => {
        const listItem = document.createElement('li');
        listItem.innerHTML = `<strong>${item.name}</strong><br/>${generateLinks(item.apis)}`;
        itemsList.appendChild(listItem);
    });
});

function generateLinks(apis) {
    return apis.map(api => `<a href="${api[1]}" target="_blank">${api[0]}</a>`).join('<br/>');
}
