function requestPromise(request) {
    return new Promise((resolve, reject) => {
        request.onsuccess = () => resolve(request.result);
        request.onerror = () => reject(request.error);
    });
}

async function openDatabase(dbName) {
    const request = indexedDB.open(dbName);
    return requestPromise(request);
}

async function getAllFromStore(db, storeName) {
    const transaction = db.transaction(storeName, "readonly");
    const objectStore = transaction.objectStore(storeName);
    return requestPromise(objectStore.getAll());
}

try {
    const db = await openDatabase(arguments[0]);
    const data = await getAllFromStore(db, arguments[1]);
    return JSON.stringify(data);
} catch (error) {
    console.log("Failed to extract session:", error)
    return null;
}