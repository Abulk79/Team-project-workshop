const buttonTeam = document.querySelector('.dropDownTeam');
const buttonMember = document.querySelector('.dropDownMember');

buttonTeam.addEventListener('click', () => {
  document.querySelector('.hiddenTeam').classList.remove('hidden');
});

buttonMember.addEventListener('click', () => {
  document.querySelector('.hiddenMember').classList.remove('hidden');
});
