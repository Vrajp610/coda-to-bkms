export const filterValidSundays = (date) => {
    const today = new Date();
    const currentSunday = new Date(today);
    currentSunday.setDate(today.getDate() - today.getDay());

    const oneWeekAgoSunday = new Date(currentSunday);
    oneWeekAgoSunday.setDate(currentSunday.getDate() - 7);

    const twoWeeksAgoSunday = new Date(currentSunday);
    twoWeeksAgoSunday.setDate(currentSunday.getDate() - 14);

    const nextSunday = new Date(today);
    nextSunday.setDate(today.getDate() + (7 - today.getDay()));

    const allowedDates = [
        currentSunday.toDateString(),
        oneWeekAgoSunday.toDateString(),
        twoWeeksAgoSunday.toDateString(),
        nextSunday.toDateString(), 
    ];

    return date.getDay() === 0 && allowedDates.includes(date.toDateString());
};