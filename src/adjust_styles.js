/*

adjust_styles.js

Make the appearance of the Last Card table, match the Current Card table
for a more consistent appearance. The two differ because the latter is
generated in the add-on while the former comes from an internal web
service in the Anki application (and modified by scripts that are running
on the page delivered by that service.)

The strategy here is to allow the Last Card table to be produced, then scrape
all of its data, create a new table using our format, insert it into the DOM
then delete the original table.

*/


function waitForElementByXPath(path) {
   // wait for the element specified at the given XPath to be available
   return new Promise(resolve => {
      const resType = XPathResult.FIRST_ORDERED_NODE_TYPE;
      if (document.evaluate(path, document, null, resType, null).singleNodeValue) {
         return resolve(document.evaluate(path, document, null, resType, null).singleNodeValue);
      }

      const observer = new MutationObserver(mutations => {
         if (document.evaluate(path, document, null, resType, null).singleNodeValue) {
            resolve(document.evaluate(path, document, null, resType, null).singleNodeValue);
            observer.disconnect();
         }
      });

      observer.observe(document.body, {
         childList: true,
         subtree: true
      });
   });
}

async function adjustAppearance() {
   console.log("adjust_styles.js script loaded!");

   // get the last card table and wait about 20ms
   // this is a little fragile, but seemingly necessary
   let wait = new Promise((resolve, reject) => {
      setTimeout(() => resolve(1), 20)
   });
   await wait;
   // get the last card table
   let targetPath = "//*[contains(@id,'cardinfo-')]/div/div/div/table";
   const lc_table = await waitForElementByXPath(targetPath)

   // iterate over rows, accumulating headers and data
   headers = []; data = [];
   Array.from(lc_table.children).forEach(row => { 
      const targetHeader = row.querySelector('th');
      headers.push(targetHeader.textContent);

      const targetCell = row.querySelector('td');
      data.push(targetCell.textContent);
   });

   // create new table
   var newLastCardTable = document.createElement('table');
   newLastCardTable.style.width = "100%";

   for(let i = 0; i < headers.length; i++) {
      row = document.createElement('tr');
      headerCell = document.createElement('td');
      headerCell.width = "35%";
      headerCell.align = "left";
      headerCell.style.paddingRight = "3px";
      boldHeaderElement = document.createElement('b')
      boldHeaderElement.textContent = headers[i];
      headerCell.appendChild(boldHeaderElement);
      row.appendChild(headerCell);

      dataCell = document.createElement('td');
      dataCell.textContent = data[i];
      row.appendChild(dataCell);

      newLastCardTable.appendChild(row);
   }

   // insert new last card table and remove the old last card table
   const resType = XPathResult.FIRST_ORDERED_NODE_TYPE;
   lastCardParentDivPath = "//*[contains(@id,'cardinfo-')]"
   lastCardParentDiv = document.evaluate(lastCardParentDivPath, document, null, resType, null).singleNodeValue;
   var insertionPoint = lastCardParentDiv.parentNode;
   insertionPoint.insertBefore(newLastCardTable, lastCardParentDiv);
   insertionPoint.removeChild(lastCardParentDiv);

   return;
}

if (document.readyState !== 'loading') {
   adjustAppearance();
} else {
   document.addEventListener('DOMContentLoaded', adjustAppearance);
}
