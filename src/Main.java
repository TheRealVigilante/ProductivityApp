import java.io.IOException;
import java.util.Scanner;

public class Main {
        public static class ClassSelector {
        public static void selectClass(int choice) throws IOException, InterruptedException {
            switch (choice) {
                case 1:
                    System.out.println("Choose an option for Create Block:");
                    System.out.println("a. Block for a time");
                    System.out.println("b. Block After");
                    System.out.println("c. Set A daily Limit");
                    System.out.println("d. Set password");
                    Scanner scanner = new Scanner(System.in);
                    char blockChoice = scanner.next().charAt(0);
                    scanner.close();
                    switch (blockChoice) {
                        case 'a':
                            TimeRangeLock.TimeLock();
                            break;
                        case 'b':
                            TimeRangeLock.AfterTimeLock();
                            break;
                        case 'c':
                            DailyLimitLock.DailyLock();
                            break;
                        case 'd':
                            PasswordGUI.PasswordLock();
                            break;
                        default:
                            System.out.println("Invalid option for Create Block");
                            break;
                    }
                    break;
                case 2:
                    System.out.println("Edit Block is Under Development");
                    System.exit(0);
                    break;
                case 3:
                    System.out.println("Choose an option for Create Deadlock:");
                    System.out.println("a. Block for a time(Under Development)");
                    System.out.println("b. Block After(Under Development)");
                    System.out.println("c. Set a daily Limit");
                    System.out.println("d. Set password(Under Development)");
                    Scanner scanner2 = new Scanner(System.in);
                    char deadlockChoice = scanner2.next().charAt(0);
                    scanner2.close();
                    switch (deadlockChoice) {
                        case 'a', 'b', 'd':
                            System.out.println("Under Development Currently");
                            System.exit(0);
                            break;
                        case 'c':
                            DeadDailyLimitLock.DailyLock();
                            break;
                        default:
                            System.out.println("Invalid option for Create Deadlock");
                            break;
                    }
                    break;
                default:
                    System.out.println("Invalid choice");
                    break;
            }
        }
    }


    public static void main(String[] args) throws IOException, InterruptedException {
        Scanner scanner = new Scanner(System.in);

        System.out.println("Choose a number:");
        System.out.println("1. Create Block");
        System.out.println("2. Edit Block (Under Development)");
        System.out.println("3. Create Deadlock");

        int choice = scanner.nextInt();
        ClassSelector.selectClass(choice);
        scanner.close();
    }
}
