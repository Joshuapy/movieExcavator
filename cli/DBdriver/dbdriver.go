// sqlite3 驱动封装
// joshua
// 2023.9.21

package DBdriver

import (
	"database/sql"
	"fmt"
	"log"
	"os"

	_ "github.com/mattn/go-sqlite3"
)

var dbfile string = os.Getenv("MOVIE_DB")

func CheckImportOk() string {
	return "ok"
}
func getConn() *sql.DB {
	if dbfile == "" {
		log.Fatal("env MOVIE_DB is empty!")
	}
	db, err := sql.Open("sqlite3", dbfile)
	if err != nil {
		log.Fatal(err)
	}
	return db
}

func queryRowsAndPrint(sql_string string) {
	db := getConn()
	defer db.Close()

	rows, err := db.Query(sql_string)
	if err != nil {
		log.Fatal(err)
	}

	for rows.Next() {
		var hash, title, tags, create_time string
		var score float64
		err := rows.Scan(&hash, &title, &tags, &score, &create_time)
		if err != nil {
			log.Fatal(err)
		}
		fmt.Printf("%s | %-30s | %-.2f|%s| %s\n", hash, title, score, create_time, tags)
	}

}

func QueryStatusCount() {
	sql_string := "select status, count(status) from movie group by status;"
	db := getConn()
	defer db.Close()

	var count_like int
	var count_unlike int
	var count_downloading int
	var count_downloaded int
	var total int

	rows, err := db.Query(sql_string)
	if err != nil {
		log.Fatal(err)
	}
	for rows.Next() {
		var status, count int
		err := rows.Scan(&status, &count)
		if err != nil {
			log.Fatal(err)
		}

		switch status {
		case 1:
			count_unlike = count
		case 2:
			count_like = count
		case 3:
			count_downloading = count
		case 4:
			count_downloaded = count
		}
	}
	total = count_like + count_unlike + count_downloading + count_downloaded

	fmt.Println("Total:", total)
	fmt.Println("喜欢的电影:", count_like)
	fmt.Println("忽略的电影:", count_unlike)
	fmt.Println("下载中:", count_downloading)
	fmt.Println("下载完成:", count_downloaded)
}

func ShowDownloadingMovies() {
	sql_string := "select hash, title, tags, score, create_time from movie where status = 3;"
	queryRowsAndPrint(sql_string)
}

func ShowUnlinkedMovies(limit int) {
	sql_temp := "select hash, title, tags, score, create_time from movie where status = 1  order by create_time desc limit %d;"
	sql_string := fmt.Sprintf(sql_temp, limit)
	queryRowsAndPrint(sql_string)
}

func ShowDoneMovies(limit int) {
	sql_temp := "select hash, title, tags, score, create_time from movie where status = 4 order by create_time desc limit %d;"
	sql_string := fmt.Sprintf(sql_temp, limit)
	queryRowsAndPrint(sql_string)
}

func SetStatus(hashes []string, status int) {
	var placeholder string
	for i := 0; i < len(hashes); i++ {
		if i == 0 {
			placeholder += "?"
		} else {
			placeholder += ", ?"
		}
	}
	sql_temp := "update movie set status = ? where hash in (%s);"
	sql_temp_with_placeholder := fmt.Sprintf(sql_temp, placeholder)

	values := make([]interface{}, 0, 6)
	values = append(values, status)
	for _, v := range hashes {
		values = append(values, v)
	}

	db := getConn()
	defer db.Close()
	res, err := db.Exec(sql_temp_with_placeholder, values...)
	if err != nil {
		log.Fatal(err)
	}
	n, err := res.RowsAffected()
	if err != nil {
		log.Fatal(err)
	}
	fmt.Printf("成功设置%d条数据\n", n)
}
