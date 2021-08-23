export const csvFile = {
  name: "emis/data-001.csv",
  id: "abc1",
  url: "/api/v2/releases/file/abc1",
  user: "exampleuser",
  date: "2021-01-01T10:11:12.131415+00:00",
  sha256: "sha1",
  size: 1231,
  is_deleted: false,
  shortName: "data-001.csv",
};

export const pngFile = {
  name: "emis/image-001.png",
  id: "abc2",
  url: "/api/v2/releases/file/abc2",
  user: "exampleuser",
  date: "2021-01-01T10:11:12.131415+00:00",
  sha256: "sha2",
  size: 1232,
  is_deleted: false,
  shortName: "image-001.png",
};

export const txtFile = {
  name: "emis/text-001.txt",
  id: "abc3",
  url: "/api/v2/releases/file/abc3",
  user: "exampleuser",
  date: "2021-01-01T10:11:12.131415+00:00",
  sha256: "sha3",
  size: 1233,
  is_deleted: false,
  shortName: "text-001.txt",
};

export const htmlFile = {
  name: "emis/webpage-001.html",
  id: "abc4",
  url: "/api/v2/releases/file/abc4",
  user: "exampleuser",
  date: "2021-01-01T10:11:12.131415+00:00",
  sha256: "sha4",
  size: 1234,
  is_deleted: false,
  shortName: "webpage-001.html",
};

export const jsFile = {
  name: "emis/javascript-001.js",
  id: "abc5",
  url: "/api/v2/releases/file/abc5",
  user: "exampleuser",
  date: "2021-01-01T10:11:12.131415+00:00",
  sha256: "sha5",
  size: 1235,
  is_deleted: false,
  shortName: "javascript-001.js",
};

export const jsonFile = {
  name: "emis/json-001.json",
  id: "abc6",
  url: "/api/v2/releases/file/abc6",
  user: "exampleuser",
  date: "2021-01-01T10:11:12.131415+00:00",
  sha256: "sha6",
  size: 1236,
  is_deleted: false,
  shortName: "json-001.json",
};

export const fileList = [csvFile, pngFile, txtFile, htmlFile];

export const blankFile = {
  name: "",
  id: "",
  url: "",
  user: "",
  date: "",
  sha256: "",
  size: "",
  is_deleted: "",
  shortName: "",
};

export const csvExample = `"gradually","worried","cold","field","burn","by"
"silent","beneath","unknown","basket","slabs","inside"
"conversation","memory","yellow","front","guess","arrangement"
"order","firm","process","fly","gift","excellent"
"art","fog","appearance","point","has","bend"
"search","exist","weight","if","lift","bell"
"aside","off","exchange","prepare","hunter","select"`;

export const pngExample = "data:image/png;base64,W29iamVjdCBPYmplY3Rd";

export const txtExample = "Hello world";

export const htmlExample = "<h1>Hello world!</h1>";

export const jsonExample = { example: "JSON" };
