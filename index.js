import nano from "nano";


// thsis function takes the list of revisions and removes any deleted or not 'ok' ones.
// returns a flat array of document objects
let filterList = function(list,excluderev) {
    let retVal = [];
    for (let i in list) {
        if (list[i].ok && !list[i].ok._deleted) {
            if (!excluderev || (excluderev && list[i].ok._rev !== excluderev)) {
                retVal.push(list[i].ok);
            }
        }
    }
    return retVal;
};
// convert the incoming array of document to an array of deletions - {_id:"x",_rev:"y",_deleted:true}
var convertToDeletions = function(list) {
    let retVal = [];
    for (let i in list) {
        let obj = { _id:list[i]._id, _rev:list[i]._rev, _deleted: true };
        retVal.push(obj);
    }
    return retVal;
};
function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

let nano_ = nano("https://pouchdb.usedevelopment.com");
const db = nano_.db.use('gdbscraperdb');

function demo() {
    let res = db.view("checkconflicts", "new-view");
    let reply = '';

    let updateRow = async function(row){

        let successFn = function(result){
            // remove 'deleted' leaf nodes from the list
            let docList = filterList(result);
            // if the there is only <=1 revision left, the document is either deleted
            // or not conflicted; either way, we're done
            if (docList.length <= 1) {
                console.log("Document is not conflicted.");
            }
            for (let o of docList) {
                if (typeof o["is_junk"] === "boolean") {
                    let index = docList.indexOf(o);
                    if (index > -1) {
                        docList.splice(index, 1);
                    }
                }
            }
            docList = convertToDeletions(docList);
            // now we can delete the unwanted revisions
            db.bulk({docs: docList}).then(r => {
                console.log("doc updated");
                return true;
            });
        };

        let failureFn = function(error){
            if (error) {
                console.log(error);
                console.log("Document could not be fetched");
                return false;
            }
        };

        let p = db.get(row['id'], {open_revs: 'all'});
        p.then(successFn, failureFn);
        return p;
    };

    res.then(async (unk) => {
        reply = unk;
        console.log(reply['rows'].length);
        for (let row of reply['rows']) {
            let success = await updateRow(row);
            console.log(success);
            // return;
        }
    });
}
let t = demo();

// copy the contents of object b into object a
var objmerge = function(a,b) {
    for (let i in b) {
        if (i !== "_id" && i !== "_rev") {
            a[i] = b[i];
        }
    }
    return a;
};

// In a database 'db' (a nano object), that has document with id 'docid', resolve the
// conflicts by choosing the revision with the highest field 'fieldname'.
var latestWins = function(db, docid, fieldname, callback) {

    // fetch the document with open_revs=all
    db.get(docid, {open_revs:'all'}, function(err, data) {

        // return if document isn't there
        if (err) {
            return callback("Document could not be fetched");
        }

        // remove 'deleted' leaf nodes from the list
        var doclist = filterList(data);

        // if the there is only <=1 revision left, the document is either deleted
        // or not conflcited; either way, we're done
        if (doclist.length <= 1) {
            return callback("Document is not conflicted.");
        }

        // sort the array of documents by the supplied fieldname
        // our winner will be the last object in the sorted array
        doclist.sort(function(a, b ){ return a[fieldname]-b[fieldname]});
        var last=doclist.pop(); // remove the winning revision from the array

        // turn the remaining leaf nodes into deletions
        doclist = convertToDeletions(doclist);

        // now we can delete the unwanted revisions
        db.bulk({docs: doclist}, callback);

    });
};

// In a database 'db' (a nano object), that has document with id 'docid', resolve the
// conflicts by merging all of the conflicting revisions together(!)
var merge = function(db, docid, callback) {
    var winner = null;

    // fetch the document to establish the current winning revision
    db.get(docid, function(err,data) {
        // return if document isn't there
        if (err) {
            return callback("Document could not be fetched");
        }
        winner = data;

        // fetch the document with open_revs=all
        db.get(docid, {open_revs:'all'}, function(err, data) {

            // remove 'deleted' leaf nodes from the list and the winning revision
            var doclist = filterList(data, winner._rev);

            // if the there is only <=1 revision left, the document  not conflcited
            if (doclist.length <= 1) {
                return callback("Document is not conflicted.");
            }

            // merge the losing revisions' contents into the winner's
            for(var i in doclist) {
                var loser = doclist[i];
                winner = objmerge(winner, loser);
            }

            // turn the losing leaf nodes into deletions
            doclist = convertToDeletions(doclist);

            // add our merged winners
            doclist.push(winner);

            // now we can deleted the unwanted revisions and create a new winner
            db.bulk({docs: doclist}, callback);
        });
    });
};
